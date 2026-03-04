import { Box, Paper } from '@mui/material';
import BlockRoundedIcon from '@mui/icons-material/BlockRounded';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ReactElement } from 'react';

const Container = styled.div`
  padding: 20px;
`;
const Icon = styled(BlockRoundedIcon)`
  && {
    font-size: 100px;
  }
`;
const PaperContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  color: rgba(0, 0, 0, 0.38);
  padding: 70px;
  font-size: 50px;
  height: calc(100vh - 104px);
`;
const SmallerText = styled.div`
  font-size: 16px;
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
    <Container>
      <Paper>
        <PaperContainer>
          <Icon />
          <Box>{t('Permission Denied')}</Box>
          <SmallerText>
            {t('Ask the Administrator to get access to this page')}
          </SmallerText>
          <SmallerText>Permission:</SmallerText>
          <SmallerText>{permissionText}</SmallerText>
        </PaperContainer>
      </Paper>
    </Container>
  );
}
