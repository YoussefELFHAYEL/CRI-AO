/**
 * CRI-RSK Chatbot — RTL detection utility.
 * Detects if text contains significant Arabic characters.
 */

const ARABIC_RANGE = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]/g;

export function isRtlText(text) {
  if (!text) return false;
  const arabicMatches = text.match(ARABIC_RANGE);
  if (!arabicMatches) return false;
  const nonSpace = text.replace(/\s/g, '');
  return arabicMatches.length / nonSpace.length > 0.3;
}

export function getTextDirection(text) {
  return isRtlText(text) ? 'rtl' : 'ltr';
}
