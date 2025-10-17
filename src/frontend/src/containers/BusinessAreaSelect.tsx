import { MenuItem, Select } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  ReactElement,
  useMemo,
  useCallback,
  useState,
  useEffect,
  useRef,
} from 'react';
import { RestService } from '@restgenerated/index';
import { useQuery, useQueryClient } from '@tanstack/react-query';

const CountrySelect = styled(Select)`
  && {
    width: ${({ theme }) => theme.spacing(58)};
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

export function BusinessAreaSelect(): ReactElement {
  const { businessAreaSlug, programSlug } = useBaseUrl();

  const [selectedBusinessArea, setSelectedBusinessArea] = useState<string>(
    businessAreaSlug || '',
  );

  const isInitialMount = useRef(true);

  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }

    if (businessAreaSlug && businessAreaSlug !== selectedBusinessArea) {
      setSelectedBusinessArea(businessAreaSlug);
    }
  }, [businessAreaSlug, selectedBusinessArea]);

  const { data } = useQuery({
    queryKey: ['businessAreasProfile', businessAreaSlug, programSlug],
    queryFn: () => {
      return RestService.restBusinessAreasUsersProfileRetrieve({
        businessAreaSlug,
        program: programSlug === 'all' ? undefined : programSlug,
      });
    },
    staleTime: 15 * 60 * 1000, // Data is considered fresh for 15 minutes (business areas don't change often)
    gcTime: 60 * 60 * 1000, // Keep unused data in cache for 1 hour
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
  });

  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const onChange = useCallback(
    (e): void => {
      const newBusinessArea = e.target.value;
      setSelectedBusinessArea(newBusinessArea);
      queryClient.clear();
      if (newBusinessArea === 'global') {
        navigate('/global/programs/all/country-dashboard');
      } else {
        navigate(`/${newBusinessArea}/programs/all/list`);
      }
    },
    [queryClient, navigate],
  );

  const businessAreaOptions = useMemo(() => {
    if (!data?.businessAreas) return [];

    return data.businessAreas.map((each) => (
      <MenuItem key={each.slug} value={each.slug}>
        {each.name}
      </MenuItem>
    ));
  }, [data?.businessAreas]);

  return (
    <CountrySelect
      variant="filled"
      value={selectedBusinessArea}
      onChange={onChange}
    >
      {businessAreaOptions}
    </CountrySelect>
  );
}
