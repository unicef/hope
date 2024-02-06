import React, { useRef } from 'react';
import Button from '@mui/material/Button';

export function UploadButton({
  children,
  handleChange,
  ...otherProps
}): React.ReactElement {
  const inputRef = useRef<HTMLInputElement>(null);

  const onClickHandler = () => {
    inputRef.current.click();
  };
  const onChangeHandler = (event) => {
    handleChange(event.currentTarget.files[0], null);
  };
  return (
    <>
      <Button onClick={onClickHandler} {...otherProps}>
        {children}
      </Button>
      <input
        ref={inputRef}
        accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        type="file"
        style={{ display: 'none' }}
        onChange={onChangeHandler}
      />
    </>
  );
}
