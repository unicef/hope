import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import {
  ProgramStatus,
  useBusinessAreaDataQuery,
  useProgrammeChoiceDataQuery,
  useProgramQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { ProgramDetails } from '@components/programs/ProgramDetails/ProgramDetails';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { usePermissions } from '../../../hooks/usePermissions';
import { isPermissionDeniedError } from '@utils/utils';
import { CashPlanTable } from '../../tables/payments/CashPlanTable';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';
import { ProgramDetailsPageHeader } from '../headers/ProgramDetailsPageHeader';

const Container = styled.div`
  && {
    display: flex;
    flex-direction: column;
    min-width: 100%;
  }
`;

const TableWrapper = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  padding: 20px;
  padding-bottom: 0;
`;

const NoCashPlansContainer = styled.div`
  margin-top: ${({ theme }) => theme.spacing(30)}px;
`;
const NoCashPlansTitle = styled.div`
  color: rgba(0, 0, 0, 0.38);
  font-size: 24px;
  line-height: 28px;
  text-align: center;
`;
const NoCashPlansSubTitle = styled.div`
  color: rgba(0, 0, 0, 0.38);
  font-size: 16px;
  line-height: 19px;
  text-align: center;
`;

export function ProgramDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const { data, loading, error } = useProgramQuery({
    variables: { id },
    fetchPolicy: 'network-only',
  });
  const { businessArea } = useBaseUrl();
  const { data: businessAreaData, loading: businessAreaDataLoading } =
    useBusinessAreaDataQuery({
      variables: { businessAreaSlug: businessArea },
    });
  const { data: choices, loading: choicesLoading } =
    useProgrammeChoiceDataQuery();
  const permissions = usePermissions();

  if (loading || choicesLoading || businessAreaDataLoading)
    return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data?.program || !choices || !businessAreaData || permissions === null)
    return null;

  const { program } = data;
  return (
    <div>
      <ProgramDetailsPageHeader
        program={program}
        canActivate={hasPermissions(
          PERMISSIONS.PROGRAMME_ACTIVATE,
          permissions,
        )}
        canEdit={hasPermissions(PERMISSIONS.PROGRAMME_UPDATE, permissions)}
        canRemove={hasPermissions(PERMISSIONS.PROGRAMME_REMOVE, permissions)}
        canFinish={hasPermissions(PERMISSIONS.PROGRAMME_FINISH, permissions)}
        canDuplicate={hasPermissions(
          PERMISSIONS.PROGRAMME_DUPLICATE,
          permissions,
        )}
        isPaymentPlanApplicable={
          businessAreaData.businessArea.isPaymentPlanApplicable
        }
      />
      <Container>
        <ProgramDetails program={program} choices={choices} />
        {program.status === ProgramStatus.Draft ? (
          <NoCashPlansContainer>
            <NoCashPlansTitle>
              {t('To see more details please Activate your Programme')}
            </NoCashPlansTitle>
            <NoCashPlansSubTitle>
              {t(
                'All data will be pushed to CashAssist. You can edit this plan even if it is active.',
              )}
            </NoCashPlansSubTitle>
          </NoCashPlansContainer>
        ) : (
          <TableWrapper>
            <CashPlanTable program={program} />
          </TableWrapper>
        )}
        {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
          <UniversalActivityLogTable objectId={program.id} />
        )}
      </Container>
    </div>
  );
}
