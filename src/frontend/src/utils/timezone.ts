const OFFSET_RE = /(Z|[+-]\d{2}:\d{2})$/;

export function isDateOnly(value: string): boolean {
  return /^\d{4}-\d{2}-\d{2}$/.test(value);
}

export function parseInstant(value: string): Date | null {
  if (!value) return null;
  let normalized = value;
  if (!OFFSET_RE.test(value)) {
    normalized = `${value}Z`;
    if (import.meta.env.DEV) {
      console.warn(
        `[timezone] "${value}" has no UTC offset; treating it as UTC. The backend should emit a timezone-aware datetime.`,
      );
    }
  }
  const date = new Date(normalized);
  return Number.isNaN(date.getTime()) ? null : date;
}

const formatterCache = new Map<string, Intl.DateTimeFormat>();

export function getFormatter(
  timeZone: string,
  mode: 'date' | 'dateTime',
): Intl.DateTimeFormat {
  const cacheKey = `${timeZone}|${mode}`;
  const cached = formatterCache.get(cacheKey);
  if (cached) return cached;

  const options: Intl.DateTimeFormatOptions =
    mode === 'dateTime'
      ? {
          day: 'numeric',
          month: 'short',
          year: 'numeric',
          hour: 'numeric',
          minute: '2-digit',
          hour12: true,
          timeZone,
        }
      : {
          day: 'numeric',
          month: 'short',
          year: 'numeric',
          timeZone,
        };

  let formatter: Intl.DateTimeFormat;
  try {
    formatter = new Intl.DateTimeFormat('en-GB', options);
  } catch {
    formatter = new Intl.DateTimeFormat('en-GB', { ...options, timeZone: 'UTC' });
  }
  formatterCache.set(cacheKey, formatter);
  return formatter;
}

// Assembled from parts (not `.format()`) so the output matches the existing
// date-fns `d MMM yyyy` / `d MMM yyyy h:mm a` byte-for-byte — locale formatting
// inserts commas and lowercases am/pm in ways `.format()` alone can't avoid.
export function formatInstant(
  date: Date,
  timeZone: string,
  mode: 'date' | 'dateTime',
): string {
  const parts = getFormatter(timeZone, mode).formatToParts(date);
  const get = (type: string): string =>
    parts.find((part) => part.type === type)?.value ?? '';

  const datePart = `${get('day')} ${get('month')} ${get('year')}`;
  if (mode === 'date') return datePart;

  return `${datePart} ${get('hour')}:${get('minute')} ${get('dayPeriod').toUpperCase()}`;
}

export function formatTooltip(date: Date, timeZone: string): string {
  return `${formatInstant(date, timeZone, 'dateTime')} (${timeZone})`;
}
