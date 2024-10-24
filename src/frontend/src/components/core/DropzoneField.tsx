/* eslint-disable react-hooks/exhaustive-deps */
import { Box } from '@mui/material';
import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { LoadingComponent } from './LoadingComponent';

interface DropzoneContainerProps {
  disabled: boolean;
}

interface DropzoneFieldProps {
  onChange: (acceptedFiles: File[]) => void;
  loading: boolean;
  dontShowFilename: boolean;
  accepts?: { [key: string]: string[] };
}

const DropzoneContainer = styled.div<DropzoneContainerProps>`
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
  margin-top: ${({ theme }) => theme.spacing(5)};
  padding: ${({ theme }) => theme.spacing(5)};
  cursor: pointer;
  ${({ disabled }) => (disabled ? 'filter: grayscale(100%);' : '')}
`;

export const DropzoneField = ({
  onChange,
  loading,
  dontShowFilename,
  accepts = {
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': [
      '.xlsx',
    ],
  },
}: DropzoneFieldProps): React.ReactElement => {
  const { t } = useTranslation();
  const onDrop = useCallback((acceptedFiles: File[]) => {
    onChange(acceptedFiles);
  }, []);

  const { getRootProps, getInputProps, acceptedFiles } = useDropzone({
    disabled: loading,
    accept: accepts,
    onDrop,
  });

  const acceptedFilename =
    acceptedFiles.length > 0 ? acceptedFiles[0].name : null;

  return (
    <Box display="flex" justifyContent="center" p={5}>
      <DropzoneContainer {...getRootProps()} disabled={loading}>
        <LoadingComponent isLoading={loading} absolute />
        <input
          {...getInputProps()}
          accept={Object.values(accepts).flat().join(',')}
          data-cy="file-input"
        />
        {dontShowFilename || !acceptedFilename
          ? t('UPLOAD FILE')
          : acceptedFilename}
      </DropzoneContainer>
    </Box>
  );
};
