import RotateRightIcon from '@mui/icons-material/RotateRight';
import { IconButton } from '@mui/material';
import { Dispatch, SetStateAction, ReactElement } from 'react';

export function RotateImg({
  turnAngle,
  setTurnAngle,
}: {
  turnAngle: number;
  setTurnAngle: Dispatch<SetStateAction<number>>;
}): ReactElement {
  const handleRotateImg = (): void => {
    document
      .getElementById('modalImg')
      .setAttribute('style', `transform: rotate(${turnAngle}deg)`);
    setTurnAngle((prev) => prev + 90);
  };

  return (
    <IconButton data-cy="button-rotate-image" onClick={() => handleRotateImg()}>
      <RotateRightIcon />
    </IconButton>
  );
}
