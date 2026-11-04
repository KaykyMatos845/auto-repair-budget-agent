"""Local-only CPU car-damage proposals, with image quality checks and class-wise NMS."""
import base64
import hashlib
import importlib
from functools import lru_cache
import io
import json
import os
from pathlib import Path
import threading
import warnings

ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / 'model_manifest.json').read_text())
LABELS = [
    ('Para-brisa dianteiro', 'possível dano no vidro'),
    ('Farol', 'possível dano no farol'),
    ('Vidro traseiro', 'possível dano no vidro'),
    ('Soleira', 'possível dano na soleira'),
    ('Retrovisor', 'possível dano no retrovisor'),
    ('Lanterna', 'possível dano na lanterna'),
    ('Capô', 'possível amassado'),
    ('Tampa do porta-malas', 'possível amassado'),
    ('Porta', 'possível amassado'),
    ('Paralama', 'possível amassado'),
    ('Para-choque dianteiro', 'possível amassado'),
    ('Painel lateral traseiro', 'possível amassado'),
    ('Para-choque traseiro', 'possível amassado'),
    ('Teto', 'possível amassado'),
]
_session = None
_lock = threading.Lock()


class LocalVisionError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def model_path():
    return Path(os.environ.get('LOCAL_MODEL_DIR', ROOT / 'models')) / MANIFEST['filename']


@lru_cache(maxsize=1)
def dependency_issues():
    """Import native modules too: an installed wheel can still have broken DLLs."""
    issues = []
    for name in ['numpy', 'PIL.Image', 'cv2', 'onnxruntime']:
        try:
            importlib.import_module(name)
        except Exception as error:
            issues.append({'module': name,
                           'kind': 'missing' if isinstance(error, ModuleNotFoundError) else 'load',
                           'detail': str(error)[:600]})
    return issues


def require_dependencies():
    issues = dependency_issues()
    if issues:
        for issue in issues:
            print(f"[Dependência {issue['module']}] {issue['detail']}", flush=True)
        modules = ', '.join(issue['module'] for issue in issues)
        code = 'LOCAL_RUNTIME_LOAD' if any(issue['kind'] == 'load' for issue in issues) else 'LOCAL_DEPENDENCIES'
        raise LocalVisionError(code, f'O ambiente Python não conseguiu carregar: {modules}. '
                               'Feche o servidor e inicie com npm start para preparar o ambiente correto. '
                               'Se persistir, confira o motivo no terminal.')


def local_health():
    issues = dependency_issues()
    try:
        installed = model_path().is_file()
    except OSError:
        installed = False
    return {'status': 'ok', 'provider': 'local', 'dependenciesInstalled': not issues,
            'dependencyIssues': [{'module': issue['module'], 'kind': issue['kind']} for issue in issues],
            'modelInstalled': installed, 'modelLoaded': _session is not None,
            'modelName': MANIFEST['repository'], 'networkRequiredForAnalysis': False,
            'note': 'Presença de arquivo não comprova integridade; verificação ocorre ao carregar.'}


def get_session():
    global _session
    if _session is not None:
        return _session
    require_dependencies()
    import onnxruntime as ort
    path = model_path()
    try:
        if not path.is_file():
            raise LocalVisionError('LOCAL_MODEL_MISSING', 'Instale o modelo uma vez: python scripts/download_model.py')
        with path.open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != MANIFEST['sha256']:
                raise LocalVisionError('LOCAL_MODEL_INTEGRITY', 'Pesos do modelo inválidos. Execute novamente python scripts/download_model.py.')
    except OSError as error:
        raise LocalVisionError('LOCAL_MODEL_ACCESS', 'O servidor não consegue ler os pesos. Confira as permissões de LOCAL_MODEL_DIR e model.onnx.') from error
    options = ort.SessionOptions()
    options.intra_op_num_threads = max(1, min(4, os.cpu_count() or 1))
    options.inter_op_num_threads = 1
    try:
        ort.disable_telemetry_events()
        _session = ort.InferenceSession(str(path), sess_options=options, providers=['CPUExecutionProvider'])
    except Exception as error:
        raise LocalVisionError('LOCAL_MODEL_LOAD', 'Não foi possível carregar o modelo local. Confira as dependências e os pesos instalados.') from error
    return _session


def decode_photo(encoded):
    import cv2
    import numpy as np
    from PIL import Image, ImageOps, UnidentifiedImageError
    try:
        # Protect allocation before converting a compressed image to RGB.
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(base64.b64decode(encoded, validate=True))) as source:
                if source.width * source.height > 24_000_000:
                    raise ValueError('Foto acima de 24 megapixels; reduza a resolução.')
                image = ImageOps.exif_transpose(source).convert('RGB')
                image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
    except (ValueError, OSError, UnidentifiedImageError, Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
        raise LocalVisionError('LOCAL_IMAGE_INVALID', 'Foto inválida ou grande demais. Envie JPEG, PNG ou WebP com até 24 megapixels.') from error
    quality_image = image.copy()
    quality_image.thumbnail((1024, 1024))
    gray = cv2.cvtColor(np.asarray(quality_image), cv2.COLOR_RGB2GRAY)
    brightness = float(gray.mean())
    focus = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    issues = []
    if min(image.size) < 320:
        issues.append('resolução muito baixa; use pelo menos 320 pixels no lado menor')
    if brightness < 30:
        issues.append('foto muito escura')
    elif brightness > 235:
        issues.append('foto muito clara ou superexposta')
    if focus < 20:
        issues.append('pouco detalhe ou possível desfoque')
    return image, issues, {'brightness': round(brightness, 1), 'focusVariance': round(focus, 1)}


def letterbox(image):
    import numpy as np
    from PIL import Image
    size = MANIFEST['input_size']
    width, height = image.size
    scale = min(size / width, size / height)
    new_width, new_height = round(width * scale), round(height * scale)
    xpad, ypad = (size - new_width) // 2, (size - new_height) // 2
    canvas = Image.new('RGB', (size, size), (114, 114, 114))
    canvas.paste(image.resize((new_width, new_height), Image.Resampling.BILINEAR), (xpad, ypad))
    tensor = np.asarray(canvas, dtype=np.float32).transpose(2, 0, 1)[None] / 255.0
    return np.ascontiguousarray(tensor), (scale, xpad, ypad, width, height)


def parse_detections(output, geometry, threshold):
    import numpy as np
    rows = np.asarray(output)
    if rows.ndim != 3 or rows.shape[0] != 1 or rows.shape[1] != 18:
        raise LocalVisionError('LOCAL_MODEL_OUTPUT', 'Saída do modelo incompatível com as 14 classes esperadas.')
    predictions = rows[0].T
    classes = predictions[:, 4:].argmax(axis=1)
    scores = predictions[:, 4:].max(axis=1)
    candidates = np.flatnonzero(np.isfinite(scores) & (scores >= threshold))
    # Bound CPU work even on unexpected/noisy outputs.
    candidates = sorted(candidates, key=lambda i: float(scores[i]), reverse=True)[:300]
    scale, xpad, ypad, width, height = geometry
    detections = []
    for index in candidates:
        cx, cy, w, h = predictions[index, :4]
        if not np.isfinite([cx, cy, w, h]).all() or w <= 0 or h <= 0:
            continue
        x1, x2 = np.clip([(cx - w / 2 - xpad) / scale, (cx + w / 2 - xpad) / scale], 0, width)
        y1, y2 = np.clip([(cy - h / 2 - ypad) / scale, (cy + h / 2 - ypad) / scale], 0, height)
        if x2 <= x1 or y2 <= y1:
            continue
        label = int(classes[index])
        box = [float(x1), float(y1), float(x2), float(y2)]
        detections.append({'classId': label, 'score': round(float(scores[index]), 4), 'xyxy': box,
                           'box': [round(float(y1 / height * 100), 2), round(float(x1 / width * 100), 2),
                                   round(float(y2 / height * 100), 2), round(float(x2 / width * 100), 2)]})
    return suppress_detections(detections)


def suppress_detections(detections):
    kept = []
    for detection in sorted(detections, key=lambda item: item['score'], reverse=True):
        x1, y1, x2, y2 = detection['xyxy']
        suppressed = False
        for previous in kept:
            if previous['classId'] != detection['classId']:
                continue
            a, b, c, d = previous['xyxy']
            intersection = max(0, min(c, x2) - max(a, x1)) * max(0, min(d, y2) - max(b, y1))
            union = (c - a) * (d - b) + (x2 - x1) * (y2 - y1) - intersection
            if union > 0 and intersection / union > 0.45:
                suppressed = True
                break
        if not suppressed:
            kept.append(detection)
        if len(kept) >= 20:
            break
    return kept


def detect_photo(session, image, threshold, detailed):
    """Run a full view plus at most four overlapping views, sequentially on CPU."""
    width, height = image.size
    windows = [(0, 0, width, height)]
    if detailed and max(image.size) > MANIFEST['input_size']:
        crop_width, crop_height = round(width * 0.7), round(height * 0.7)
        windows.extend((x, y, crop_width, crop_height)
                       for y in [0, height - crop_height] for x in [0, width - crop_width])
    detections = []
    for x, y, w, h in windows:
        tensor, geometry = letterbox(image.crop((x, y, x + w, y + h)))
        output = session.run(None, {session.get_inputs()[0].name: tensor})[0]
        for detection in parse_detections(output, geometry, threshold):
            a, b, c, d = detection['xyxy']
            # Crop boundaries can turn one part into several fragments. Leave those
            # to the full view or another overlapping crop; never merge across photos.
            if ((x > 0 and a < 8) or (y > 0 and b < 8) or
                    (x + w < width and c > w - 8) or (y + h < height and d > h - 8)):
                continue
            detection['xyxy'] = [a + x, b + y, c + x, d + y]
            detection['box'] = [round((b + y) / height * 100, 2), round((a + x) / width * 100, 2),
                                round((d + y) / height * 100, 2), round((c + x) / width * 100, 2)]
            detections.append(detection)
    return suppress_detections(detections), len(windows)


def analyze_local(images, vehicle_hint=None, detailed=True):
    if not _lock.acquire(timeout=1):
        raise LocalVisionError('LOCAL_BUSY', 'O detector local está ocupado. Aguarde a análise atual terminar.')
    try:
        return _analyze(images, vehicle_hint or {}, detailed)
    finally:
        _lock.release()


def _analyze(images, vehicle_hint, detailed):
    require_dependencies()
    try:
        threshold = float(os.environ.get('LOCAL_CONFIDENCE', '0.60'))
        if not 0.1 <= threshold <= 0.95:
            raise ValueError()
    except ValueError as error:
        raise LocalVisionError('LOCAL_CONFIG', 'LOCAL_CONFIDENCE deve estar entre 0.10 e 0.95.') from error
    parts, issues, metrics = [], [], []
    usable = False
    inference_passes = 0
    for image_index, encoded in enumerate(images):
        image, problems, quality = decode_photo(encoded)
        metrics.append({'imageIndex': image_index, **quality, 'usable': not problems})
        if problems:
            issues.extend(f'Foto {image_index + 1}: {problem}.' for problem in problems)
            continue
        usable = True
        session = get_session()
        detections, passes = detect_photo(session, image, threshold, detailed)
        inference_passes += passes
        for detection in detections:
            part_name, damage = LABELS[detection['classId']]
            parts.append({'name': part_name, 'category': 'Sugestão do detector local',
                          'evidence': f'{damage.capitalize()} indicado na região marcada da foto {image_index + 1}. Sugestão automática, não confirmação.',
                          'imageIndex': image_index, 'box': detection['box'], 'detectorScore': detection['score']})
    # The shared output contract bounds the proposal list to 30 items.
    return {'vehicle': {field: vehicle_hint.get(field, '') for field in ['brand', 'model', 'year', 'color']},
            'imageQuality': {'usable': usable, 'issues': issues, 'metrics': metrics},
            'limitations': ['Detector local de 14 classes; pode errar ou não detectar um dano.',
                            'Não reconhece marca, modelo, ano, riscos finos ou defeitos mecânicos e internos.',
                            'Score do detector não é uma probabilidade calibrada de acerto.',
                            'Fotos diferentes podem mostrar a mesma peça; remova itens duplicados antes de orçar.',
                            'Fotos com qualidade insuficiente não foram analisadas.'] if issues else
                           ['Detector local de 14 classes; pode errar ou não detectar um dano.',
                            'Não reconhece marca, modelo, ano, riscos finos ou defeitos mecânicos e internos.',
                            'Score do detector não é uma probabilidade calibrada de acerto.',
                            'Fotos diferentes podem mostrar a mesma peça; remova itens duplicados antes de orçar.'],
            'damageAnalysis': {'summary': f'{min(len(parts), 30)} região(ões) suspeita(s) sugerida(s) pelo detector local. Confirme presencialmente.', 'parts': parts[:30]},
            'analysisSettings': {'detailed': detailed, 'inferencePasses': inference_passes,
                                 'confidenceThreshold': threshold},
            '_providerModel': MANIFEST['repository'], '_modelChanged': False}
