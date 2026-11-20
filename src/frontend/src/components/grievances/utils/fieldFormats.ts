export const PHONE_NUMBER_FIELDS = [
  'phone_no',
  'phone_no_alternative',
  'payment_delivery_phone_no',
];

export const EMAIL_FIELDS = ['email'];

export const PHONE_NUMBER_FORMAT_ERROR =
  'Enter a valid phone number with the country code';
export const EMAIL_FORMAT_ERROR = 'Enter a valid email address';
export const NEGATIVE_NUMBER_ERROR = 'Value cannot be negative';

// Fail-fast checks only; the backend serializers stay the source of truth
const PHONE_NUMBER_REGEX = /^\+[1-9]\d{6,14}$/;
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const isBlank = (value): boolean =>
  value === undefined || value === null || value === '';

export function getFieldFormatError(
  fieldName: string,
  fieldValue,
  fieldType?: string,
): string | undefined {
  if (isBlank(fieldValue)) {
    return undefined;
  }
  if (PHONE_NUMBER_FIELDS.includes(fieldName)) {
    const digits = String(fieldValue).replace(/[\s\-().]/g, '');
    return PHONE_NUMBER_REGEX.test(digits)
      ? undefined
      : PHONE_NUMBER_FORMAT_ERROR;
  }
  if (EMAIL_FIELDS.includes(fieldName)) {
    return EMAIL_REGEX.test(String(fieldValue).trim())
      ? undefined
      : EMAIL_FORMAT_ERROR;
  }
  if (fieldType === 'INTEGER' && Number(fieldValue) < 0) {
    return NEGATIVE_NUMBER_ERROR;
  }
  return undefined;
}
