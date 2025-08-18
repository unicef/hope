import { useTranslation } from 'react-i18next';
import { useField } from 'formik';
import {
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Select,
} from '@mui/material';
import styled from 'styled-components';
import CircularProgress from '@mui/material/CircularProgress';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';

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

export function KoboProjectSelect(): ReactElement {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const [field] = useField('koboAssetId');
  const {
    data: koboProjectsData,
    isLoading: loading,
    error,
  } = useQuery({
    queryKey: ['koboProjects', businessArea],
    queryFn: async () => {
      return RestService.restBusinessAreasAllKoboProjectsCreate({
        slug: businessArea,
      });
    },
    enabled: !!businessArea,
  });
  
  const koboProjects = koboProjectsData || [];

  const formatError = (errorObject): string | null => {
    if (errorObject) {
      return errorObject.message || 'Error loading projects';
    }
    return null;
  };

  return (
    <>
      <FormControl variant="outlined">
        <StyledInputLabel size="small">{t('Select Project')}</StyledInputLabel>
        <ComboBox
          {...field}
          variant="outlined"
          size="small"
          label={t('Kobo Project')}
          disabled={loading}
          fullWidth
          endAdornment={
            <>
              {loading ? (
                <CircularProgressContainer>
                  <CircularProgress color="inherit" size={20} />{' '}
                </CircularProgressContainer>
              ) : null}
            </>
          }
          data-cy="kobo-project-select"
        >
          {koboProjects.map((item) => (
            <MenuItem key={item.id} value={item.id}>
              {item.name}
            </MenuItem>
          ))}
        </ComboBox>
      </FormControl>
      <FormHelperText error>{formatError(error)}</FormHelperText>
    </>
  );
}
