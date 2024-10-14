import * as React from 'react';
import { format } from 'date-fns';
import { DATE_FORMAT, DATE_FORMAT_LONG } from '../../config';

export interface Props {
  children: string;
  withTime?: boolean;
}

export function UniversalMoment({
  children,
  withTime,
}: Props): React.ReactElement {
  const dateFormat = withTime ? DATE_FORMAT_LONG : DATE_FORMAT;
  const date = children ? new Date(children) : null;
  const formattedDate = date ? format(date, dateFormat) : '-';
  const dateTime = date ? date.getTime().toString() : '';

  return date ? (
    <time dateTime={dateTime}>{formattedDate}</time>
  ) : (
    <>{formattedDate}</>
  );
}
