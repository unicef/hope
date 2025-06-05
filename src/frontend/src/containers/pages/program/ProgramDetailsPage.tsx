import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { ProgramDetails } from '@components/programs/ProgramDetails/ProgramDetails';
import ProgramCyclesTableProgramDetails from '@containers/tables/ProgramCycle/ProgramCyclesTableProgramDetails';
import { useProgrammeChoiceDataQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { BusinessArea } from '@restgenerated/models/BusinessArea';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { Status791Enum } from '@restgenerated/models/Status791Enum';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { isPermissionDeniedError } from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';
import { ProgramDetailsPageHeader } from '../headers/ProgramDetailsPageHeader';
import { useHopeDetailsQuery } from '@hooks/useHopeDetailsQuery';

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
  padding: 20px 20px 0;
`;

const NoCashPlansContainer = styled.div`
  margin-top: 120px;
`;
const NoCashPlansTitle = styled.div`
  color: rgba(0, 0, 0, 0.38);
  font-size: 24px;
  line-height: 28px;
  text-align: center;
`;

function ProgramDetailsPage(): ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const { businessArea } = useBaseUrl();

  const {
    data: program,
    isLoading: loading,
    error,
  } = useHopeDetailsQuery<ProgramDetail>(
    id,
    RestService.restBusinessAreasProgramsRetrieve,
    {},
  );

  const { data: businessAreaData, isLoading: businessAreaDataLoading } =
    useQuery<BusinessArea>({
      queryKey: ['businessArea', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasRetrieve({
          slug: businessArea,
        }),
    });

  const { data: choices, loading: choicesLoading } =
    useProgrammeChoiceDataQuery();
  const permissions = usePermissions();

  if (loading || choicesLoading || businessAreaDataLoading)
    return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!choices || !businessAreaData || permissions === null) return null;

  const canFinish = hasPermissions(PERMISSIONS.PROGRAMME_FINISH, permissions);
  return (
    <>
      <ProgramDetailsPageHeader
        program={program}
        canActivate={hasPermissions(
          PERMISSIONS.PROGRAMME_ACTIVATE,
          permissions,
        )}
        canEdit={hasPermissions(PERMISSIONS.PROGRAMME_UPDATE, permissions)}
        canRemove={hasPermissions(PERMISSIONS.PROGRAMME_REMOVE, permissions)}
        canFinish={canFinish}
        canDuplicate={hasPermissions(
          PERMISSIONS.PROGRAMME_DUPLICATE,
          permissions,
        )}
      />
      <Container>
        <ProgramDetails program={program} choices={choices} />
        {program?.status === Status791Enum.DRAFT ? (
          <NoCashPlansContainer>
            <NoCashPlansTitle>
              {t('Activate the Programme to create a Cycle')}
            </NoCashPlansTitle>
          </NoCashPlansContainer>
        ) : (
          <TableWrapper>
            <ProgramCyclesTableProgramDetails program={program} />
          </TableWrapper>
        )}
        {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
          <UniversalActivityLogTable objectId={program.id} />
        )}
      </Container>
    </>
  );
}

export default withErrorBoundary(ProgramDetailsPage, 'ProgramDetailsPage');
