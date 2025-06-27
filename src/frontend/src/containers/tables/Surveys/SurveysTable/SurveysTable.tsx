import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AllSurveysQueryVariables,
  SurveyNode,
  SurveysChoiceDataQuery,
  useAllSurveysQuery,
} from '@generated/graphql';
import { TableWrapper } from '@components/core/TableWrapper';
import { choicesToDict, dateToIsoString } from '@utils/utils';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { UniversalTable } from '../../UniversalTable';
import { headCells } from './SurveysTableHeadCells';
import { SurveysTableRow } from './SurveysTableRow';

interface SurveysTableProps {
  filter;
  canViewDetails: boolean;
  choicesData: SurveysChoiceDataQuery;
}

export function SurveysTable({
  filter,
  canViewDetails,
  choicesData,
}: SurveysTableProps): ReactElement {
  const { programId } = useBaseUrl();
  const { t } = useTranslation();

  const initialVariables: AllSurveysQueryVariables = {
    search: filter.search,
    paymentPlan: filter.targetPopulation || '',
    createdBy: filter.createdBy || '',
    program: programId,
    createdAtRange: JSON.stringify({
      min: dateToIsoString(filter.createdAtRangeMin, 'startOfDay'),
      max: dateToIsoString(filter.createdAtRangeMax, 'endOfDay'),
    }),
  };
  const categoryDict = choicesToDict(choicesData.surveyCategoryChoices);

  return (
    <TableWrapper>
      <UniversalTable<SurveyNode, AllSurveysQueryVariables>
        headCells={headCells}
        title={t('Surveys List')}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllSurveysQuery}
        queriedObjectName="allSurveys"
        defaultOrderBy="createdAt"
        defaultOrderDirection="desc"
        initialVariables={initialVariables}
        renderRow={(row) => (
          <SurveysTableRow
            key={row.id}
            survey={row}
            canViewDetails={canViewDetails}
            categoryDict={categoryDict}
          />
        )}
      />
    </TableWrapper>
  );
}
