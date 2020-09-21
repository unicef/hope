import React from 'react';
import Moment from 'react-moment';
import { DATE_FORMAT, DATE_FORMAT_LONG } from '../config';

export interface Props {
  children: string;
  withTime?: boolean;
}

export function UniversalMoment({
  children,
  withTime,
}: Props): React.ReactElement {
  return (
    <Moment format={withTime ? DATE_FORMAT_LONG : DATE_FORMAT}>
      {children}
    </Moment>
  );
}
