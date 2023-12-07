import { MenuItem, Select } from '@material-ui/core';
import React, { useCallback, useEffect, useRef } from 'react';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import {
  AllProgramsForChoicesQuery,
  useAllProgramsForChoicesQuery,
} from '../__generated__/graphql';
import { LoadingComponent } from '../components/core/LoadingComponent';
import { useBaseUrl } from '../hooks/useBaseUrl';
import { useProgramContext } from '../programContext';
import { isProgramNodeUuidFormat } from '../utils/utils';

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
    fetchPolicy: 'network-only',
  });

  const isMounted = useRef(false);

  useEffect(() => {
    isMounted.current = true;
    return () => {
      isMounted.current = false;
    };
  }, []);

  const isOneOfAvailableProgramsId = useCallback(
    (id: string): boolean => {
      return data?.allPrograms.edges.some((each) => each.node.id === id);
    },
    [data],
  );

  const getCurrentProgram = useCallback(():
    | AllProgramsForChoicesQuery['allPrograms']['edges'][number]['node']
    | null => {
    const obj = data?.allPrograms.edges.find((el) => el.node.id === programId);
    return obj ? obj.node : null;
  }, [data, programId]);

  useEffect(() => {
    if (programId !== 'all') {
      const program = getCurrentProgram();
      if (!selectedProgram || selectedProgram?.id !== programId) {
        if (program && isMounted.current) {
          const {
            id,
            name,
            status,
            individualDataNeeded,
            dataCollectingType,
          } = program;

          setSelectedProgram({
            id,
            name,
            status,
            individualDataNeeded,
            dataCollectingType: {
              id: dataCollectingType?.id,
              householdFiltersAvailable:
                dataCollectingType?.householdFiltersAvailable,
              individualFiltersAvailable:
                dataCollectingType?.individualFiltersAvailable,
            },
          });
        }
      }
    }
  }, [programId, selectedProgram, setSelectedProgram, getCurrentProgram]);

  useEffect(() => {
    // If the programId is not in a valid format, redirect to the 404 page
    if (
      programId &&
      !isProgramNodeUuidFormat(programId) &&
      programId !== 'all'
    ) {
      history.push(`/404/${businessArea}`);
    }
    // If the programId is valid but not one of the available programs, redirect to the access denied page
    else if (
      !loading &&
      programId &&
      !isOneOfAvailableProgramsId(programId) &&
      programId !== 'all'
    ) {
      history.push(`/access-denied/${businessArea}`);
    }
  }, [programId, history, businessArea, isOneOfAvailableProgramsId, loading]);

  const onChange = (e): void => {
    if (e.target.value === 'all') {
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
      {data.allPrograms.edges
        .sort((objA, objB) => objA.node.name.localeCompare(objB.node.name))
        .map((each) => (
          <MenuItem key={each.node.id} value={each.node.id}>
            {each.node.name}
          </MenuItem>
        ))}
    </CountrySelect>
  );
};
