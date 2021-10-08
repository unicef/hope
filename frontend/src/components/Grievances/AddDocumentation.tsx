import { Box, Grid } from '@material-ui/core';
import DeleteIcon from '@material-ui/icons/Delete';
import React, { useRef } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { LookUpButton } from './LookUpButton';

const StyledBox = styled.div`
  border: 1.5px solid #043e91;
  border-radius: 5px;
  font-size: 16px;
  padding: 16px;
  background-color: #f7faff;
  cursor: pointer;
`;

const BlueText = styled.span`
  color: #033f91;
  font-weight: 500;
  font-size: 16px;
`;

const DarkGrey = styled.span`
  color: #757575;
  cursor: pointer;
`;

export const AddDocumentation = ({
  onValueChange,
  values,
}: {
  onValueChange;
  values;
}): React.ReactElement => {
  const { t } = useTranslation();
  const inputRef = useRef<HTMLInputElement>(null);

  const onClickHandler = (): void => {
    inputRef.current.click();
  };

  const onChangeHandler = (event): void => {
    onValueChange('selectedDocumentation', event.currentTarget.files);
  };

  const renderFilenames = (): React.ReactElement => {
    return (
      <>
        {values.selectedDocumentation.length &&
          Array.from(values.selectedDocumentation).map((file: File) => (
            <BlueText key={file.name}>{file.name}</BlueText>
          ))}
      </>
    );
  };

  const handleRemove = (event): void => {
    event.stopPropagation();
    onValueChange('selectedDocumentation', []);
  };
  return values.selectedDocumentation.length ? (
    <StyledBox onClick={onClickHandler}>
      <Grid alignItems='center' container>
        <Grid item xs={9}>
          <Box display='flex' flexDirection='column'>
            {renderFilenames()}
          </Box>
        </Grid>
        <Grid item xs={3}>
          <Box p={2}>
            <Grid container justify='flex-end' alignItems='center'>
              <Grid item>
                <DarkGrey>
                  <DeleteIcon
                    color='inherit'
                    fontSize='small'
                    onClick={(e) => handleRemove(e)}
                  />
                </DarkGrey>
              </Grid>
            </Grid>
          </Box>
        </Grid>
      </Grid>
      <input
        ref={inputRef}
        accept='application/pdf,application/msword,
        application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        multiple
        type='file'
        style={{ display: 'none' }}
        onChange={onChangeHandler}
      />
    </StyledBox>
  ) : (
    <>
      <LookUpButton
        addIcon
        title={t('Add Related Documentation')}
        handleClick={onClickHandler}
      />
      <input
        ref={inputRef}
        accept='application/pdf,application/msword,
        application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        multiple
        type='file'
        style={{ display: 'none' }}
        onChange={onChangeHandler}
      />
    </>
  );
};
