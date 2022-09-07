/* eslint-disable react-hooks/exhaustive-deps */
import { Box } from '@material-ui/core';
import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { LoadingComponent } from './LoadingComponent';

const DropzoneContainer = styled.div`
  width: 500px;
  height: 100px;
  background-color: rgba(2, 62, 144, 0.1);
  color: #023e90;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.5px;
  line-height: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: ${({ theme }) => theme.spacing(5)}px;
  padding: ${({ theme }) => theme.spacing(5)}px;
  cursor: pointer;
  ${({ disabled }) => (disabled ? 'filter: grayscale(100%);' : '')}
`;

export function DropzoneField({
  onChange,
  loading,
  dontShowFilename,
}): React.ReactElement {
  const { t } = useTranslation();
  const onDrop = useCallback((acceptedFiles) => {
    onChange(acceptedFiles);
  }, []);
  const { getRootProps, getInputProps, acceptedFiles } = useDropzone({
    disabled: loading,
    accept: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    onDrop,
  });
  const acceptedFilename =
    acceptedFiles.length > 0 ? acceptedFiles[0].name : null;
  return (
    <Box display='flex' justifyContent='center' p={5}>
      <DropzoneContainer {...getRootProps()} disabled={loading}>
        <LoadingComponent isLoading={loading} absolute />
        <input {...getInputProps()} data-cy='rdi-file-input' />
        {dontShowFilename || !acceptedFilename
          ? t('UPLOAD FILE')
          : acceptedFilename}
      </DropzoneContainer>
    </Box>
  );
}
