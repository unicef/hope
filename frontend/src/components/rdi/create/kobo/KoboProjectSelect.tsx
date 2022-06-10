import React from 'react';
import { useTranslation } from 'react-i18next';
import { useField } from 'formik';
import { FormControl, InputLabel, MenuItem, Select } from '@mui/material';
import styled from 'styled-components';
import CircularProgress from '@mui/material/CircularProgress';
import { useAllKoboProjectsQuery } from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';

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
  const businessArea = useBusinessArea();
  const [field] = useField('koboAssetId');
  const { data: koboProjectsData, loading } = useAllKoboProjectsQuery({
    variables: { businessAreaSlug: businessArea },
  });
  const koboProjects = koboProjectsData?.allKoboProjects?.edges || [];
  return (
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
  );
}
