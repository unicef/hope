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
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ContainerColumnWithBorder } from '../../../core/ContainerColumnWithBorder';
import { Title } from '../../../core/Title';

const GreyText = styled.p`
  color: #9e9e9e;
  font-size: 16px;
`;

const Divider = styled.div`
  border-top: 1px solid #b1b1b5;
  height: 2px;
  width: 50%;
  margin-top: 20px;
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

interface EntitlementProps {
  businessArea: string;
  permissions: string[];
}

export function Entitlement({
  businessArea,
  permissions,
}: EntitlementProps): React.ReactElement {
  const { t } = useTranslation();
  const [entitlement, setEntitlement] = useState<string>('');
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
            <Divider />
            <DividerLabel>Or</DividerLabel>
            <Divider />
          </Box>
        </Box>
      </ContainerColumnWithBorder>
    </Box>
  );
}
