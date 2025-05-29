import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  PaymentPlanBuildStatus,
  useBusinessAreaDataQuery,
} from '@generated/graphql';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { StatusBox } from '@components/core/StatusBox';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { paymentPlanBuildStatusToColor } from '@utils/utils';
import { FinalizedTargetPopulationHeaderButtons } from './FinalizedTargetPopulationHeaderButtons';
import { LockedTargetPopulationHeaderButtons } from './LockedTargetPopulationHeaderButtons';
import { OpenTargetPopulationHeaderButtons } from './OpenTargetPopulationHeaderButtons';
import { AdminButton } from '@core/AdminButton';
import { ReactElement } from 'react';

const HeaderWrapper = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  div {
    margin: 0 0 0 ${({ theme }) => theme.spacing(3)};
  }
`;
const StatusWrapper = styled.div`
  display: flex;
  flex-direction: row;
`;

export interface TargetPopulationPageHeaderProps {
  paymentPlan;
  canEdit: boolean;
  canRemove: boolean;
  canDuplicate: boolean;
  canLock: boolean;
  canUnlock: boolean;
  canSend: boolean;
}

export function TargetPopulationPageHeader({
  paymentPlan,
  canEdit,
  canRemove,
  canDuplicate,
  canLock,
  canUnlock,
  canSend,
}: TargetPopulationPageHeaderProps): ReactElement {
  const { t } = useTranslation();
  const { baseUrl, businessArea } = useBaseUrl();
  const { data: businessAreaData, loading: businessAreaDataLoading } =
    useBusinessAreaDataQuery({
      variables: { businessAreaSlug: businessArea },
    });
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Targeting',
      to: `/${baseUrl}/target-population/`,
    },
  ];

  if (!businessAreaData) return null;
  if (businessAreaDataLoading) return <LoadingComponent />;

  let buttons;

  switch (paymentPlan.status) {
    case PaymentPlanStatusEnum.TP_OPEN:
      buttons = (
        <OpenTargetPopulationHeaderButtons
          targetPopulation={paymentPlan}
          canDuplicate={canDuplicate}
          canRemove={canRemove}
          canEdit={canEdit}
          canLock={canLock}
        />
      );
      break;
    case PaymentPlanStatusEnum.TP_LOCKED:
    case PaymentPlanStatusEnum.STEFICON_COMPLETED:
    case PaymentPlanStatusEnum.STEFICON_ERROR:
    case PaymentPlanStatusEnum.STEFICON_RUN:
      buttons = (
        <LockedTargetPopulationHeaderButtons
          targetPopulation={paymentPlan}
          canDuplicate={canDuplicate}
          canUnlock={canUnlock}
          canSend={canSend}
          businessAreaData={businessAreaData}
        />
      );
      break;
    default:
      // Ready for Cash Assist, Processing, Ready, Accepted
      buttons = (
        <FinalizedTargetPopulationHeaderButtons
          targetPopulation={paymentPlan}
          canDuplicate={canDuplicate}
        />
      );
      break;
  }
  return (
    <PageHeader
      title={
        <HeaderWrapper>
          {t(`${paymentPlan.name}`)}
          {paymentPlan.buildStatus !== PaymentPlanBuildStatus.Ok && (
            <StatusWrapper>
              <StatusBox
                status={paymentPlan.buildStatus}
                statusToColor={paymentPlanBuildStatusToColor}
              />
            </StatusWrapper>
          )}
        </HeaderWrapper>
      }
      breadCrumbs={breadCrumbsItems}
      flags={<AdminButton adminUrl={paymentPlan.adminUrl} />}
    >
      {buttons}
    </PageHeader>
  );
}
