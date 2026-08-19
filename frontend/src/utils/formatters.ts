/**
 * Utility functions for formatting currencies, locations, and real estate units.
 */

/**
 * Formats a number as Indian Rupees currency string (e.g., ₹1,24,65,981)
 */
export function formatINR(val: number): string {
  if (isNaN(val) || val === null || val === undefined) return '₹0';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(Math.round(val));
}

/**
 * Formats property price into standard Indian Denominations (Crores or Lakhs)
 * e.g., ₹1.25 Cr or ₹45.00 Lakhs
 */
export function formatIndianDenomination(val: number): {
  formatted: string;
  unit: string;
  compact: string;
} {
  if (isNaN(val) || val <= 0) {
    return { formatted: '₹0', unit: 'Rupees', compact: '₹0' };
  }

  const crores = val / 10000000;
  const lakhs = val / 100000;

  if (crores >= 1.0) {
    return {
      formatted: `₹${crores.toFixed(2)}`,
      unit: 'Crore',
      compact: `₹${crores.toFixed(2)} Cr`,
    };
  } else if (lakhs >= 1.0) {
    return {
      formatted: `₹${lakhs.toFixed(2)}`,
      unit: 'Lakhs',
      compact: `₹${lakhs.toFixed(2)} Lakhs`,
    };
  } else {
    return {
      formatted: formatINR(val),
      unit: 'Rupees',
      compact: formatINR(val),
    };
  }
}

/**
 * Formats location slugs into clean readable title strings.
 * e.g. "new-delhi" -> "New Delhi", "navi-mumbai" -> "Navi Mumbai"
 */
export function formatLocation(loc: string): string {
  if (!loc) return '';
  return loc
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

/**
 * Formats floor number to human-readable label.
 * e.g. -1 -> "Basement", 0 -> "Ground Floor", 3 -> "3rd Floor"
 */
export function formatFloor(floorNum: number, totalFloors?: number): string {
  let label = '';
  if (floorNum === -1) {
    label = 'Basement';
  } else if (floorNum === 0) {
    label = 'Ground Floor';
  } else {
    const s = ['th', 'st', 'nd', 'rd'];
    const v = floorNum % 100;
    const suffix = s[(v - 20) % 10] || s[v] || s[0];
    label = `${floorNum}${suffix} Floor`;
  }

  if (totalFloors && totalFloors > 0) {
    return `${label} of ${totalFloors}`;
  }
  return label;
}
