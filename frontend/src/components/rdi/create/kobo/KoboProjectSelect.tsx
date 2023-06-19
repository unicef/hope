import React from 'react';
import { useTranslation } from 'react-i18next';
import { useField } from 'formik';
import {
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Select,
} from '@material-ui/core';
import styled from 'styled-components';
import CircularProgress from '@material-ui/core/CircularProgress';
import { useAllKoboProjectsQuery } from '../../../../__generated__/graphql';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';

const ComboBox = styled(Select)`
  & {
    min-width: 200px;
  }
`;
const CircularProgressContainer = styled.div`
  margin-right: 40px;
`;
const StyledInputLabel = styled(InputLabel)`
  background-color: #fff;
`;

export function KoboProjectSelect(): React.ReactElement {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const [field] = useField('koboAssetId');
  const { data: koboProjectsData, loading, error } = useAllKoboProjectsQuery({
    variables: { businessAreaSlug: businessArea },
  });
  const koboProjects = koboProjectsData?.allKoboProjects?.edges || [];

  const formatError = (errorObject): string | null => {
    if (errorObject) {
      return errorObject.message.replace('GraphQL error: ', '');
    }
    return null;
  };

  return (
    <>
      <FormControl variant='outlined' margin='dense'>
        <StyledInputLabel>{t('Select Project')}</StyledInputLabel>
        <ComboBox
          {...field}
          variant='outlined'
          label={t('Kobo Project')}
          disabled={loading}
          fullWidth
          endAdornment={
            <>
              {loading ? (
                <CircularProgressContainer>
                  <CircularProgress color='inherit' size={20} />{' '}
                </CircularProgressContainer>
              ) : null}
            </>
          }
        >
          {koboProjects.map((item) => (
            <MenuItem key={item.node.id} value={item.node.id}>
              {item.node.name}
            </MenuItem>
          ))}
        </ComboBox>
      </FormControl>
      <FormHelperText error>{formatError(error)}</FormHelperText>
    </>
  );
}
