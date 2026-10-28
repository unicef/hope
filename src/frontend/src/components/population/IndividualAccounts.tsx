import { DividerLine } from '@components/core/DividerLine';
import { LoadingComponent } from '@core/LoadingComponent';
import type { FC } from 'react';
import { LabelizedField } from '@components/core/LabelizedField';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import { Title } from '@core/Title';
import { usePermissions } from '@hooks/usePermissions';
import type { Theme } from '@mui/material';
import { Paper, Typography } from '@mui/material';
import type { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { renderSomethingOrDash, splitCamelCase } from '@utils/utils';
import { t } from 'i18next';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { useProgramContext } from 'src/programContext';
import {
  ResponsiveGrid,
  ResponsiveGridContainer,
  SECTION_PADDING,
} from 'src/responsive';
import styled from 'styled-components';
import { useArrayToDict } from '@hooks/useArrayToDict';
import type { Account } from '@restgenerated/models/Account';
import type { AccountAttachment } from '@restgenerated/models/AccountAttachment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { useQuery } from '@tanstack/react-query';

const IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png'];

const isImage = (file: string): boolean =>
  IMAGE_EXTENSIONS.includes(file.split('.').pop()?.toLowerCase() ?? '');

const AttachmentField: FC<{ attachment: AccountAttachment }> = ({
  attachment,
}) => {
  const label = attachment.title || t('Attachment');
  return (
    <ResponsiveGrid size="quarter" mobileSize="half">
      <LabelizedField label={label}>
        {isImage(attachment.file) ? (
          <PhotoModal src={attachment.file} title={label} />
        ) : (
          <a href={attachment.file} target="_blank" rel="noopener noreferrer">
            {t('Download')}
          </a>
        )}
      </LabelizedField>
    </ResponsiveGrid>
  );
};

interface IndividualAccountsProps {
  individual: IndividualDetail;
}

const Overview = styled(Paper)<{ theme?: Theme }>`
  margin-top: ${({ theme }) => theme.spacing(6)};
  margin-bottom: ${({ theme }) => theme.spacing(4)};
`;
interface AccountItemProps {
  account: Account;
  lastItem?: boolean;
  accountFinancialInstitutionsDict:
    | {
        [p: string]: any;
      }
    | {
        [p: number]: any;
      };
}
const AccountItem: FC<AccountItemProps> = ({
  account,
  lastItem,
  accountFinancialInstitutionsDict,
}) => {
  const dataFields = account.dataFields;
  return (
    <ResponsiveGrid size="full" key={account.id}>
      <Typography variant="h6">{account.name}</Typography>
      <ResponsiveGridContainer spacing={3}>
        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Financial Institution')}>
            {renderSomethingOrDash(
              accountFinancialInstitutionsDict[
                account.financialInstitution ?? ''
              ],
            )}
          </LabelizedField>
        </ResponsiveGrid>

        <ResponsiveGrid size="quarter" mobileSize="half">
          <LabelizedField label={t('Number')}>
            {renderSomethingOrDash(account.number)}
          </LabelizedField>
        </ResponsiveGrid>
        {dataFields.map((field, idx) => {
          return (
            <ResponsiveGrid key={idx} size="quarter" mobileSize="half">
              <LabelizedField label={splitCamelCase(field.key)}>
                {renderSomethingOrDash(field.value)}
              </LabelizedField>
            </ResponsiveGrid>
          );
        })}
        {account.attachments?.map((attachment) => (
          <AttachmentField key={attachment.id} attachment={attachment} />
        ))}
      </ResponsiveGridContainer>
      {!lastItem && <DividerLine />}
    </ResponsiveGrid>
  );
};

export const IndividualAccounts: FC<IndividualAccountsProps> = ({
  individual,
}) => {
  const permissions = usePermissions();
  const canViewDeliveryMechanisms = hasPermissions(
    PERMISSIONS.POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION,
    permissions,
  );
  const { selectedProgram } = useProgramContext();
  const { businessAreaSlug } = useBaseUrl();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const {
    data: financialInstitutionChoices,
    isLoading: financialInstitutionChoicesLoading,
  } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasFinancialInstitutionsChoicesList,
      { businessAreaSlug },
    ),
    queryFn: () =>
      RestService.restBusinessAreasFinancialInstitutionsChoicesList({
        businessAreaSlug,
      }),
  });
  const accountFinancialInstitutionsDict = useArrayToDict(
    financialInstitutionChoices,
    'value',
    'name',
  );

  if (!individual?.accounts?.length || !canViewDeliveryMechanisms) {
    return null;
  }

  if (financialInstitutionChoicesLoading) {
    return <LoadingComponent />;
  }

  return (
    <Overview sx={{ padding: SECTION_PADDING }}>
      <Title>
        <Typography variant="h6">
          {t(`${beneficiaryGroup?.memberLabel} Accounts`)}
        </Typography>
      </Title>
      <ResponsiveGridContainer spacing={6}>
        {individual.accounts.map((account, index) => {
          return (
            <AccountItem
              account={account}
              key={account.id}
              lastItem={index + 1 === individual.accounts.length}
              accountFinancialInstitutionsDict={
                accountFinancialInstitutionsDict
              }
            />
          );
        })}
      </ResponsiveGridContainer>
    </Overview>
  );
};
