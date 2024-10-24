import * as React from 'react';
import { useState } from 'react';
import styled from 'styled-components';
import { useInterval } from '@hooks/useInterval';

interface ValueProps {
  missing?: boolean;
}

const Value = styled.span<ValueProps>`
  color: #253b46;
  font-size: 14px;
  line-height: 19px;
  color: ${({ missing }) => (missing ? 'red' : 'black')};
`;

export function Missing(): React.ReactElement {
  const [missing, setMissing] = useState(false);
  useInterval(() => {
    setMissing(!missing);
  }, 1000);
  return <Value missing={missing}>MISSING</Value>;
}
