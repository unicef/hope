import Tooltip from '@mui/material/Tooltip';
import { ReactElement } from 'react';
import { useTimezone } from 'src/timezoneContext';
import { formatInstant, formatTooltip, isDateOnly, parseInstant } from '@utils/timezone';

export interface Props {
  children: string;
  withTime?: boolean;
}

export function UniversalMoment({ children, withTime }: Props): ReactElement {
  const timezone = useTimezone();

  if (!children) {
    return <>-</>;
  }

  if (isDateOnly(children)) {
    // True calendar date: parse as literal UTC midnight, never through the
    // offset-less-datetime path (that path exists for real timestamps and warns).
    const dateOnly = new Date(`${children}T00:00:00Z`);
    return (
      <time dateTime={children}>{formatInstant(dateOnly, 'UTC', 'date')}</time>
    );
  }

  const date = parseInstant(children);
  if (!date) {
    return <>-</>;
  }

  const mode = withTime ? 'dateTime' : 'date';
  const formattedDate = formatInstant(date, timezone, mode);
  const tooltip = formatTooltip(date, timezone);

  return (
    <Tooltip title={tooltip}>
      <time dateTime={date.toISOString()}>{formattedDate}</time>
    </Tooltip>
  );
}
