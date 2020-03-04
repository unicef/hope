import React, { useState } from 'react';
import styled from 'styled-components';
import { Button } from '@material-ui/core';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

export function EditTargetPopulationHeader(): React.ReactElement {
  return (
    <div>
      <ButtonContainer>
        <Button variant='contained' color='primary' disabled>
          Save
        </Button>
      </ButtonContainer>
    </div>
  );
}
