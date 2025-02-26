import { Box } from '@mui/material';
import styled from 'styled-components';
import { UniversalMoment } from '@core/UniversalMoment';
import { PaymentPlanQuery } from '@generated/graphql';
import { MessageDialog } from './MessageDialog';
import { ReactElement } from 'react';

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
  approvals: PaymentPlanQuery['paymentPlan']['approvalProcess']['edges'][number]['node']['actions']['approval'];
}

export function GreyInfoCard({
  topMessage,
  topDate,
  approvals,
}: GreyInfoCardProps): ReactElement {
  const mappedApprovals = approvals?.map((action) => {
    const { info, createdAt, comment, createdBy } = action;
    return (
      info && (
        <Box alignItems="center" display="flex" key={createdAt}>
          {info}
          <Box ml={1}>
            <GreyText>
              on <UniversalMoment>{createdAt}</UniversalMoment>
            </GreyText>
          </Box>
          <Box p={1} ml={1}>
            {comment ? (
              <MessageDialog
                comment={comment}
                author={createdBy}
                date={createdAt}
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
    <Box display="flex" flexDirection="column">
      <Box p={3}>
        <GreyTitle>
          {topMessage} on
          <UniversalMoment>{topDate}</UniversalMoment>
        </GreyTitle>
      </Box>
      <GreyBox
        display="flex"
        flexDirection="column"
        alignItems="center"
        ml={3}
        mr={3}
        p={3}
      >
        {mappedApprovals}
      </GreyBox>
    </Box>
  );
}
