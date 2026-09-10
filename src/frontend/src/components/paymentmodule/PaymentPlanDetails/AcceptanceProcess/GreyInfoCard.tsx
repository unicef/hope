import { Box } from '@mui/material';
import styled from 'styled-components';
import { UniversalMoment } from '@core/UniversalMoment';
import { MessageDialog } from './MessageDialog';
import type { ReactElement } from 'react';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

const GreyText = styled.div`
  color: #9e9e9e;
`;

const GreyTitle = styled.div`
  color: #7c8990;
  text-transform: uppercase;
  font-size: 12px;
`;

const IconPlaceholder = styled.div`
  width: 16px;
  height: 16px;
`;

const GreyBox = styled(Box)`
  background-color: #f4f5f6;
`;

interface GreyInfoCardProps {
  topMessage: string;
  topDate: string;
  approvals: PaymentPlanDetail['approvalProcess'][number]['actions'];
  author?: string;
}

export function GreyInfoCard({
  topMessage,
  topDate,
  approvals,
  author,
}: GreyInfoCardProps): ReactElement {
  const mappedApprovals = approvals?.map((action) => {
    const { info, createdAt, comment } = action;
    return (
      info && (
        <Box
          key={createdAt}
          sx={{
            alignItems: 'center',
            display: 'flex',
          }}
        >
          {info}
          <Box
            sx={{
              ml: 1,
            }}
          >
            <GreyText>
              on <UniversalMoment>{createdAt}</UniversalMoment>
            </GreyText>
          </Box>
          <Box
            sx={{
              p: 1,
              ml: 1,
            }}
          >
            {comment ? (
              <MessageDialog
                comment={comment}
                date={createdAt}
                author={author}
              />
            ) : (
              <IconPlaceholder />
            )}
          </Box>
        </Box>
      )
    );
  });

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Box
        sx={{
          p: 3,
        }}
      >
        <GreyTitle>
          {topMessage} on <UniversalMoment>{topDate}</UniversalMoment>
        </GreyTitle>
      </Box>
      <GreyBox
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          ml: 3,
          mr: 3,
          p: 3,
        }}
      >
        {mappedApprovals}
      </GreyBox>
    </Box>
  );
}
