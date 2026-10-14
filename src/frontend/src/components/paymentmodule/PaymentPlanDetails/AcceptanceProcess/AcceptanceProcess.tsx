import { Box, Button, Typography } from '@mui/material';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import type { ReactElement, ReactNode } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { Title } from '@core/Title';
import { AcceptanceProcessRow } from './AcceptanceProcessRow';
import withErrorBoundary from '@components/core/withErrorBoundary';
import type { ApprovalProcess } from '@restgenerated/models/ApprovalProcess';

const ButtonContainer = styled(Box)`
  width: 200px;
`;

export interface AcceptanceProcessClosure {
  closedBy: string | null;
  closedDate: string;
}

interface AcceptanceProcessProps {
  approvalProcess: ApprovalProcess[] | undefined;
  closure?: AcceptanceProcessClosure | null;
  headerAction?: ReactNode;
}

function AcceptanceProcess({
  approvalProcess,
  closure = null,
  headerAction,
}: AcceptanceProcessProps): ReactElement {
  const { t } = useTranslation();
  const [showAll, setShowAll] = useState(false);

  if (!approvalProcess?.length) {
    return null;
  }

  // The backend orders approval processes newest first.
  const shown = showAll ? approvalProcess : [approvalProcess[0]];

  return (
    <Box
      sx={{
        m: 5,
      }}
      data-cy="acceptance-process"
    >
      <ContainerColumnWithBorder>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            mt: 4,
          }}
        >
          <Title>
            <Typography variant="h6">{t('Acceptance Process')}</Typography>
          </Title>
          {headerAction}
        </Box>
        {shown.map((item, index) => (
          <AcceptanceProcessRow
            key={item.sentForApprovalDate ?? index}
            acceptanceProcess={item}
            closure={index === 0 ? closure : null}
            showDivider={approvalProcess.length > 1}
          />
        ))}
        {approvalProcess.length > 1 && (
          <ButtonContainer>
            <Button
              variant="outlined"
              color="primary"
              onClick={() => setShowAll(!showAll)}
              endIcon={showAll ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            >
              {showAll ? t('HIDE') : t('SHOW PREVIOUS')}
            </Button>
          </ButtonContainer>
        )}
      </ContainerColumnWithBorder>
    </Box>
  );
}

export default withErrorBoundary(AcceptanceProcess, 'AcceptanceProcess');
