import React from 'react';
import Moment from 'react-moment';
import { DATE_FORMAT } from '../config';

export interface Props {
  children: string;
}

export function UniversalMoment({ children }: Props): React.ReactElement {
  return children ? <Moment format={DATE_FORMAT}>{children}</Moment> : <>-</>;
}
