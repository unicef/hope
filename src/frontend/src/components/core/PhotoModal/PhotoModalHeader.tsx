import { Box, DialogTitle } from '@mui/material';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { RotateImg } from './RotateImg';
import { Dispatch, SetStateAction, ReactElement } from 'react';

export function PhotoModalHeader({
  turnAngle,
  setTurnAngle,
  title,
  showRotate,
}: {
  turnAngle: number;
  setTurnAngle: Dispatch<SetStateAction<number>>;
  title: string;
  showRotate: boolean;
}): ReactElement {
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
}
