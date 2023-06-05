import React from 'react';
import styled from 'styled-components';

const FieldBorderDiv = styled.div`
  padding: 0 ${({ theme }) => theme.spacing(2)}px;
  border-color: ${(props) => props.color};
  border-left-width: 2px;
  border-left-style: solid;
`;

export const FieldBorder = ({ color, children }): React.ReactElement => {
  return <FieldBorderDiv color={color}>{children}</FieldBorderDiv>;
};
