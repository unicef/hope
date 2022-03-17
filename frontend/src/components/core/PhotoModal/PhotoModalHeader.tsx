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
  showRotate,
}: {
  turnAngle: number;
  setTurnAngle: React.Dispatch<React.SetStateAction<number>>;
  title: string;
  showRotate: boolean;
}): React.ReactElement => {
  return (
    <DialogTitleWrapper>
      <DialogTitle id='scroll-dialog-title'>
        <Box display='flex' justifyContent='space-between' alignItems='center'>
          <span>{title}</span>
          {showRotate ? (
            <RotateImg turnAngle={turnAngle} setTurnAngle={setTurnAngle} />
          ) : null}
        </Box>
      </DialogTitle>
    </DialogTitleWrapper>
  );
};
