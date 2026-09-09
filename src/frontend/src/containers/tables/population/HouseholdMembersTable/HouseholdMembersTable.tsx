import { BlackLink } from '@components/core/BlackLink';
import { Bold } from '@components/core/Bold';
import { StatusBox } from '@components/core/StatusBox';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import type { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import TableCell from '@mui/material/TableCell';
import type { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import type { HouseholdMember } from '@restgenerated/models/HouseholdMember';
import type { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import type { IndividualList } from '@restgenerated/models/IndividualList';
import type { PaginatedHouseholdMemberList } from '@restgenerated/models/PaginatedHouseholdMemberList';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { useQuery } from '@tanstack/react-query';
import {
  adjustHeadCells,
  choicesToDict,
  populationStatusToColor,
  sexToCapitalize,
} from '@utils/utils';
import type { ReactElement, ReactNode } from 'react';
import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';

const headCells: HeadCell<IndividualList>[] = [
  {
    disablePadding: false,
    label: 'Individual ID',
    id: 'unicefId',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Individual',
    id: 'fullName',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Status',
    id: 'status',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Relationship to HoH',
    id: 'relationship',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Date of Birth',
    id: 'birthDate',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Gender',
    id: 'sex',
    numeric: false,
  },
];

interface HouseholdMembersTableProps {
  household: HouseholdDetail;
  choicesData: IndividualChoices;
}
export const HouseholdMembersTable = ({
  household,
  choicesData,
}: HouseholdMembersTableProps): ReactElement => {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();

  const handleClick = (row): void => {
    navigate(`/${baseUrl}/population/individuals/${row.id}`);
  };

  const relationshipChoicesDict = choicesToDict(
    choicesData?.relationshipChoices,
  );

  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const replacements = {
    unicefId: (_beneficiaryGroup) => `${_beneficiaryGroup?.memberLabel} ID`,
    fullName: (_beneficiaryGroup) => `${_beneficiaryGroup?.memberLabel}`,
    relationship: (_beneficiaryGroup) =>
      `Relationship to Head of ${_beneficiaryGroup?.groupLabel}`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  const { programId, businessArea } = useBaseUrl();

  const initialQueryVariables = useMemo(() => {
    return {
      businessAreaSlug: businessArea,
      programCode: programId,
    };
  }, [businessArea, programId]);

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const membersParams = {
    businessAreaSlug: businessArea,
    programCode: programId,
    id: household.id,
  };
  const { data, isLoading, error } = useQuery<PaginatedHouseholdMemberList>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsHouseholdsMembersList,
      membersParams,
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsMembersList(membersParams),
    enabled: !!businessArea && !!programId,
  });

  return (
    <UniversalRestTable
      title={`${beneficiaryGroup?.groupLabel} Members`}
      allowSort={false}
      headCells={adjustedHeadCells}
      data={data}
      error={error}
      isLoading={isLoading}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      renderRow={(row: HouseholdMember) => {
        const isHead = row.relationship === 'HEAD';

        const renderTableCellContent = (content: ReactNode) => {
          return isHead ? <Bold>{content}</Bold> : content;
        };

        return (
          <ClickableTableRow
            hover
            onClick={() => handleClick(row)}
            role="checkbox"
            key={row.id}
          >
            <TableCell align="left">
              {renderTableCellContent(
                <BlackLink to={`/${baseUrl}/population/individuals/${row.id}`}>
                  {row.unicefId}
                </BlackLink>,
              )}
            </TableCell>
            <TableCell align="left">
              {renderTableCellContent(row.fullName)}
            </TableCell>
            <TableCell align="left">
              <StatusBox
                status={row.status}
                statusToColor={populationStatusToColor}
              />
            </TableCell>
            <TableCell align="left">
              {renderTableCellContent(
                household?.id === row?.household?.id
                  ? relationshipChoicesDict[row.relationship ?? '']
                  : relationshipChoicesDict.NON_BENEFICIARY,
              )}
            </TableCell>
            <TableCell align="right">
              {renderTableCellContent(
                <UniversalMoment>{row.birthDate}</UniversalMoment>,
              )}
            </TableCell>
            <TableCell align="left">
              {renderTableCellContent(sexToCapitalize(row.sex))}
            </TableCell>
          </ClickableTableRow>
        );
      }}
    />
  );
};
