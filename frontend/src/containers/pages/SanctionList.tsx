/* eslint-disable react-hooks/exhaustive-deps */
import React, { useState } from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Button, Box, Paper } from '@material-ui/core';
import { useCheckAgainstSanctionListMutation } from '../../__generated__/graphql';
import { useSnackbar } from '../../hooks/useSnackBar';
import { DropzoneField } from '../../components/DropzoneField';
import { PageHeader } from '../../components/PageHeader';

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

  const ButtonsContainer = styled.div`
    width: 500px;
  `;

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
      <PageHeader title={t('Select File to Import')} />
      <Box
        display='flex'
        justifyContent='center'
        alignItems='center'
        mt={20}
        p={3}
      >
        <Paper>
          <Box display='flex' flexDirection='column' alignItems='center' p={3}>
            {importFile}
            <ButtonsContainer>
              <Box display='flex' justifyContent='space-between' p={3}>
                <Button
                  variant='text'
                  color='primary'
                  component='a'
                  href='/api/download-sanction-template'
                  onClick={(event) => {
                    /* eslint-disable-next-line @typescript-eslint/ban-ts-ignore */
                    // @ts-ignore
                    if (window.Cypress) {
                      event.preventDefault();
                    }
                  }}
                  data-cy='a-download-sanction-template'
                >
                  DOWNLOAD TEMPLATE
                </Button>
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
            </ButtonsContainer>
          </Box>
        </Paper>
      </Box>
    </>
  );
}
