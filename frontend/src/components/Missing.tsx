import React, { useState } from 'react';
import styled from 'styled-components';
import { useInterval } from '../hooks/useInterval';

const red = '#f00';
const black = '#253b46';
const Value = styled.span`
  color: #253b46;
  font-size: 14px;
  line-height: 19px;
  color: ${({ missing }) => (missing ? red : black)};
`;
export function Missing(): React.ReactElement {
  const [missing, setMissing] = useState(false);
  useInterval(() => {
    setMissing(!missing);
  }, 1000);
  return <Value missing={missing}>MISSING</Value>;
}
