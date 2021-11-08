import React from 'react';
import { Box, DialogTitle } from '@material-ui/core';
import styled from 'styled-components';
import { RotateImg } from './RotateImg';

export const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

export const PhotoModalHeader = ({
  turnAngle,
  setTurnAngle,
  title,
}: {
  turnAngle: number;
  setTurnAngle: React.Dispatch<React.SetStateAction<number>>;
  title: string;
}): React.ReactElement => {
  return (
    <DialogTitleWrapper>
      <DialogTitle id='scroll-dialog-title'>
        <Box display='flex' justifyContent='space-between' alignItems='center'>
          <span>{title}</span>
          <RotateImg turnAngle={turnAngle} setTurnAngle={setTurnAngle} />
        </Box>
      </DialogTitle>
    </DialogTitleWrapper>
  );
};
