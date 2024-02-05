import { Box, DialogTitle } from '@mui/material';
import React from 'react';
import { DialogTitleWrapper } from '../../../containers/dialogs/DialogTitleWrapper';
import { RotateImg } from './RotateImg';

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
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <span>{title}</span>
          {showRotate ? (
            <RotateImg turnAngle={turnAngle} setTurnAngle={setTurnAngle} />
          ) : null}
        </Box>
      </DialogTitle>
    </DialogTitleWrapper>
  );
};
