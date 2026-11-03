import { Box, Paper } from '@mui/material';
import BlockRoundedIcon from '@mui/icons-material/BlockRounded';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import type { ReactElement } from 'react';
import { responsiveValue } from 'src/responsive';

const Icon = styled(BlockRoundedIcon)`
  && {
    font-size: 100px;
  }
`;
const PaperContainer = styled(Box)`
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  color: rgba(0, 0, 0, 0.38);
  height: calc(100vh - 104px);
`;
const SmallerText = styled.div`
  font-size: 16px;
  overflow-wrap: anywhere;
`;

interface PermissionDeniedProp {
  permission: string | string[];
}

export function PermissionDenied({
  permission,
}: PermissionDeniedProp): ReactElement {
  const { t } = useTranslation();
  const permissionText = Array.isArray(permission)
    ? permission.join(', ')
    : permission;
  return (
    <Box sx={{ padding: responsiveValue('8px', '20px') }}>
      <Paper>
        <PaperContainer
          sx={{
            padding: responsiveValue('24px', '70px'),
            fontSize: responsiveValue('32px', '50px'),
          }}
        >
          <Icon />
          <Box>{t('Permission Denied')}</Box>
          <SmallerText>
            {t('Ask the Administrator to get access to this page')}
          </SmallerText>
          <SmallerText>Permission:</SmallerText>
          <SmallerText>{permissionText}</SmallerText>
        </PaperContainer>
      </Paper>
    </Box>
  );
}
