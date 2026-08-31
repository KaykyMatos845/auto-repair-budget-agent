export function formatCurrency(amount) {
  if (typeof amount !== 'number' || isNaN(amount)) return 'R$ 0,00';
  return amount.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  });
}

export function calculateBudgetTotals(parts = [], laborCosts = {}) {
  const bodyworkTotal = (laborCosts.bodyworkHours || 0) * (laborCosts.bodyworkRate || 0);
  const paintTotal = (laborCosts.paintPanels || 0) * (laborCosts.paintRatePerPanel || 0);
  const mechanicTotal = laborCosts.mechanicMontage || 0;

  const totalLabor = bodyworkTotal + paintTotal + mechanicTotal;

  let totalNewParts = 0;
  let totalUsedParts = 0;
  let totalSelectedParts = 0;

  parts.forEach((part) => {
    const newP = part.newPrice?.price || 0;
    const usedP = part.usedPrice?.price || 0;

    totalNewParts += newP;
    totalUsedParts += usedP;

    if (part.selectedChoice === 'new') {
      totalSelectedParts += newP;
    } else if (part.selectedChoice === 'used') {
      totalSelectedParts += usedP;
    } else if (part.selectedChoice === 'repair') {
      totalSelectedParts += 0; // Repair cost is included in labor
    }
  });

  const totalNewScenario = totalNewParts + totalLabor;
  const totalUsedScenario = totalUsedParts + totalLabor;
  const totalSelectedBudget = totalSelectedParts + totalLabor;

  const savingsAmount = Math.max(0, totalNewScenario - totalSelectedBudget);
  const maxPotentialSavings = Math.max(0, totalNewScenario - totalUsedScenario);
  const savingsPercent = totalNewScenario > 0 ? ((savingsAmount / totalNewScenario) * 100).toFixed(1) : 0;

  return {
    totalLabor,
    bodyworkTotal,
    paintTotal,
    mechanicTotal,
    totalNewParts,
    totalUsedParts,
    totalSelectedParts,
    totalNewScenario,
    totalUsedScenario,
    totalSelectedBudget,
    savingsAmount,
    maxPotentialSavings,
    savingsPercent,
  };
}
