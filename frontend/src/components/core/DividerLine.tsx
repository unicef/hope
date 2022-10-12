import React from 'react';
import styled from 'styled-components';

const DividerContainer = styled.div`
  height: 50px;
  width: 100%;
  display: flex;
  align-items: center;
`;
const Divider = styled.div`
  border-top: 1px solid #b1b1b5;
  height: 1px;
  width: 100%;
`;

export const DividerLine = (): React.ReactElement => {
  return (
    <DividerContainer>
      <Divider />
    </DividerContainer>
  );
};
