import {
  Box,
  Button,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Typography,
} from '@material-ui/core';
import Publish from '@material-ui/icons/Publish';
import GetApp from '@material-ui/icons/GetApp';
import React, { useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import styled from 'styled-components';
import { ContainerColumnWithBorder } from '../../../core/ContainerColumnWithBorder';
import { Title } from '../../../core/Title';
import { LabelizedField } from '../../../core/LabelizedField';
import { BigValue } from '../../../rdi/details/RegistrationDetails/RegistrationDetails';
import { Missing } from '../../../core/Missing';

const GreyText = styled.p`
  color: #9e9e9e;
  font-size: 16px;
`;

const GreyTextSmall = styled.p`
  color: #9e9e9e;
  font-size: 14px;
`;

const OrDivider = styled.div`
  border-top: 1px solid #b1b1b5;
  height: 2px;
  width: 50%;
  margin-top: 20px;
`;

const Divider = styled.div`
  border-top: 1px solid #b1b1b5;
  height: 20px;
`;

const DividerLabel = styled.div`
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  color: #253b46;
  text-transform: uppercase;
  padding: 5px;
  border: 1px solid #b1b1b5;
  border-radius: 50%;
  background-color: #fff;
  margin-top: 20px;
`;

const UploadIcon = styled(Publish)`
  color: #043f91;
`;
const DownloadIcon = styled(GetApp)`
  color: #043f91;
`;

const BoxWithBorderRight = styled(Box)`
  border-right: 1px solid #b1b1b5;
`;

interface EntitlementProps {
  businessArea: string;
  permissions: string[];
}

export function Entitlement({
  businessArea,
  permissions,
}: EntitlementProps): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const [entitlement, setEntitlement] = useState<string>('');
  const [file, setFile] = useState(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const entitlementChoices = [
    { name: 'USD', value: 'USD' },
    { name: 'PLN', value: 'PLN' },
  ];

  return (
    <Box m={5}>
      <ContainerColumnWithBorder>
        <Box mt={4}>
          <Title>
            <Typography variant='h6'>{t('Entitlement')}</Typography>
          </Title>
          <GreyText>{t('Select Entitlement Formula')}</GreyText>
          <Grid alignItems='center' container>
            <Grid item xs={6}>
              <FormControl variant='outlined' margin='dense' fullWidth>
                <InputLabel>{t('Entitlement Formula')}</InputLabel>
                <Select
                  value={entitlement}
                  labelWidth={180}
                  onChange={(event) =>
                    setEntitlement(event.target.value as string)
                  }
                >
                  {entitlementChoices.map((each) => (
                    <MenuItem key={each.value} value={each.value}>
                      {each.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item>
              <Box ml={2}>
                <Button
                  onClick={() => console.log('Apply')}
                  variant='contained'
                  color='primary'
                >
                  {t('Apply')}
                </Button>
              </Box>
            </Grid>
          </Grid>
          <Box display='flex' alignItems='center'>
            <OrDivider />
            <DividerLabel>Or</DividerLabel>
            <OrDivider />
          </Box>
        </Box>
        <Box display='flex'>
          <Box width='50%'>
            <BoxWithBorderRight
              display='flex'
              justifyContent='center'
              alignItems='center'
              flexDirection='column'
            >
              <Button
                color='primary'
                startIcon={<DownloadIcon />}
                onClick={() => console.log('download')}
              >
                {t('Download Template')}
              </Button>
              <GreyTextSmall>
                {t(
                  'Template contains payment list with all targeted households',
                )}
              </GreyTextSmall>
            </BoxWithBorderRight>
          </Box>
          <Box width='50%'>
            <Box
              display='flex'
              justifyContent='center'
              alignItems='center'
              flexDirection='column'
            >
              <Box>
                <Button
                  color='primary'
                  startIcon={<UploadIcon />}
                  onClick={() => inputRef.current.click()}
                >
                  {t('Upload File')}
                </Button>
                <input
                  ref={inputRef}
                  accept='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                  type='file'
                  style={{ display: 'none' }}
                  onChange={(e) => setFile(e.currentTarget.files[0])}
                />
              </Box>
              <GreyTextSmall>{file?.name || null}</GreyTextSmall>
            </Box>
          </Box>
        </Box>
        <Divider />
        <LabelizedField label={t('Total Cash Received')}>
          <BigValue>
            USD <Missing />
          </BigValue>
        </LabelizedField>
        <Button
          color='primary'
          variant='contained'
          component={Link}
          to={`/${businessArea}/payment-module/payment-plan/${id}/setup-fsp`}
        >
          {t('Set up FSP')}
        </Button>
      </ContainerColumnWithBorder>
    </Box>
  );
}
