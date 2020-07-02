/* eslint-disable react-hooks/exhaustive-deps */
import React, { useState } from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Button, Typography, Box } from '@material-ui/core';
import { useCheckAgainstSanctionListMutation } from '../../__generated__/graphql';
import { useSnackbar } from '../../hooks/useSnackBar';
import { DropzoneField } from '../../components/DropzoneField';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

export function SanctionList(): React.ReactElement {
  const { showMessage } = useSnackbar();
  const [fileToImport, setFileToImport] = useState(null);
  const [
    checkAgainstSanctionMutate,
    { data: uploadData, loading: fileLoading },
  ] = useCheckAgainstSanctionListMutation();

  const { t } = useTranslation();

  const handleImport = async (): Promise<void> => {
    const response = await checkAgainstSanctionMutate({
      variables: {
        file: fileToImport,
      },
    });
    if (response.data && !response.errors) {
      showMessage('Your import was successful!');
    } else {
      showMessage('Import failed.');
    }
  };

  let importFile = null;
  importFile = (
    <>
      <DropzoneField
        loading={fileLoading}
        onChange={(files) => {
          if (files.length === 0) {
            return;
          }
          const file = files[0];
          const fileSizeMB = file.size / (1024 * 1024);
          if (fileSizeMB > 200) {
            showMessage(
              `File size is too big. It should be under 200MB, File size is ${fileSizeMB}MB`,
            );
            return;
          }
          setFileToImport(file);
        }}
      />
    </>
  );

  return (
    <>
      <DialogTitleWrapper>
        <Typography variant='h6'>{t('Select File to Import')}</Typography>
      </DialogTitleWrapper>
      {importFile}

      <Box display='flex' justifyContent='center' p={3}>
        <Button
          type='submit'
          color='primary'
          variant='contained'
          disabled={!fileToImport}
          onClick={() => handleImport()}
          data-cy='button-import'
        >
          {t('IMPORT')}
        </Button>
      </Box>
    </>
  );
}
