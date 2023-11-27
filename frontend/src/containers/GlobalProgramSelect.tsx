import { MenuItem, Select } from '@material-ui/core';
import React, { useCallback, useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { useAllProgramsForChoicesQuery } from '../__generated__/graphql';
import { LoadingComponent } from '../components/core/LoadingComponent';
import { useBaseUrl } from '../hooks/useBaseUrl';
import {useProgramContext} from "../programContext";

const CountrySelect = styled(Select)`
  && {
    width: ${({ theme }) => theme.spacing(58)}px;
    background-color: rgba(104, 119, 127, 0.5);
    color: #e3e6e7;
    border-bottom-width: 0;
    border-radius: 4px;
    height: 40px;
  }
  .MuiFilledInput-input {
    padding: 0 10px;
    background-color: transparent;
  }
  .MuiSelect-select:focus {
    background-color: transparent;
  }
  .MuiSelect-icon {
    color: #e3e6e7;
  }
  &&:hover {
    border-bottom-width: 0;
    border-radius: 4px;
  }
  &&:hover::before {
    border-bottom-width: 0;
  }
  &&::before {
    border-bottom-width: 0;
  }
  &&::after {
    border-bottom-width: 0;
  }
  &&::after:hover {
    border-bottom-width: 0;
  }
`;

export const GlobalProgramSelect = (): React.ReactElement => {
  const { businessArea, programId } = useBaseUrl();
  const { selectedProgram, setSelectedProgram } = useProgramContext();
  const history = useHistory();
  const { data, loading } = useAllProgramsForChoicesQuery({
    variables: { businessArea, first: 100 },
    fetchPolicy: 'cache-and-network',
  });

  const isValidProgramId = useCallback(
    (id: string): boolean => {
      return data?.allPrograms.edges.some((each) => each.node.id === id);
    },
    [data],
  );

  const getCurrentProgram = () => {
  const obj = data?.allPrograms.edges.filter(
        (el) => el.node.id === programId
    )
    return obj ? obj[0].node : null
  };

  if (programId !== 'all') {
    const program = getCurrentProgram();
    if (!selectedProgram || (selectedProgram?.id !== programId)) {
      const { id, name, status, individualDataNeeded } = program;

      setSelectedProgram({
        id,
        name,
        status,
        individualDataNeeded,
        dataCollectingType: {
          id: program.dataCollectingType?.id,
          householdFiltersAvailable: program.dataCollectingType?.householdFiltersAvailable,
          individualFiltersAvailable: program.dataCollectingType?.individualFiltersAvailable,
        }
      })
    }
  }

  useEffect(() => {
    if (programId && !isValidProgramId(programId) && programId !== 'all') {
      history.push(`/${businessArea}/programs/all/list`);
    }
  }, [programId, history, businessArea, isValidProgramId]);

  const onChange = (e): void => {
    if (e.target.value === 'all' || !isValidProgramId(e.target.value)) {
      history.push(`/${businessArea}/programs/all/list`);
    } else {
      history.push(
        `/${businessArea}/programs/${e.target.value}/details/${e.target.value}`,
      );
    }
  };

  if (loading) {
    return <LoadingComponent />;
  }

  if (!data) {
    return null;
  }

  return (
    <CountrySelect
      data-cy='global-program-filter'
      variant='filled'
      value={programId}
      onChange={onChange}
    >
      <MenuItem key='all' value='all'>
        All Programmes
      </MenuItem>
      {data.allPrograms.edges.map((each) => (
        <MenuItem key={each.node.id} value={each.node.id}>
          {each.node.name}
        </MenuItem>
      ))}
    </CountrySelect>
  );
};
