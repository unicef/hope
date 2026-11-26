import CssBaseline from '@mui/material/CssBaseline';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { AppBar } from '@components/core/AppBar';
import { Drawer } from '@components/core/Drawer/Drawer';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { styled as MuiStyled } from '@mui/system';
import { theme } from 'src/theme';
import type { FC } from 'react';
import { useEffect, useState } from 'react';
import { RestService } from '@restgenerated/index';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { TimezoneProvider } from 'src/timezoneContext';
import { responsiveValue, useIsMobile } from 'src/responsive';

const Root = styled.div`
  display: flex;
  width: 100vw;
`;

const MainContent = MuiStyled('div')({
  padding: '0px 1px',
  transition: 'margin-left 225ms cubic-bezier(0, 0, 0.2, 1) 0ms',
  width: '100%',
  flexGrow: 1,
  height: '100vh',
  overflow: 'auto',
});

const AppBarSpacer = MuiStyled('div')(() => ({
  ...theme.mixins.toolbar,
}));

export const BaseHomeRouter: FC = () => {
  const isMobile = useIsMobile();
  const [desktopOpen, setDesktopOpen] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  const open = isMobile ? mobileOpen : desktopOpen;
  const { businessArea, programCode } = useBaseUrl();
  const location = useLocation();
  const navigate = useNavigate();
  const setOpen = isMobile ? setMobileOpen : setDesktopOpen;
  const handleDrawerOpen = (): void => {
    setOpen(true);
  };
  const handleDrawerClose = (): void => {
    setOpen(false);
  };

  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  const profileParams = {
    businessAreaSlug: businessArea,
    program: programCode === 'all' ? undefined : programCode,
  };

  const {
    data: profileData,
    isLoading: profileLoading,
    isError: profileError,
  } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasUsersProfileRetrieve,
      profileParams,
    ),
    queryFn: () => {
      return RestService.restBusinessAreasUsersProfileRetrieve(profileParams);
    },
    retry: false,
    staleTime: 5 * 60 * 1000, // Data is considered fresh for 5 minutes
    gcTime: 30 * 60 * 1000, // Keep unused data in cache for 30 minutes
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
  });

  if (profileError) {
    navigate('/404');
    return null;
  }

  if (!profileData || profileLoading) {
    return <LoadingComponent />;
  }

  const allBusinessAreasSlugs = profileData.businessAreas.map((el) => el.slug);
  const isBusinessAreaValid = allBusinessAreasSlugs.includes(businessArea);

  if (!isBusinessAreaValid) {
    navigate('/404');
    return null;
  }

  return (
    <TimezoneProvider timezone={profileData.effectiveTimezone ?? 'UTC'}>
      <Root>
        <CssBaseline />
        {/* On mobile the drawer overlays the page, so the app bar never shifts. */}
        <AppBar open={!isMobile && open} handleDrawerOpen={handleDrawerOpen} />
        <Drawer
          open={open}
          handleDrawerClose={handleDrawerClose}
          currentLocation={location.pathname}
          dataCy="side-nav"
        />
        <MainContent
          data-cy="main-content"
          // Lets wide content (tables) scroll inside the page instead of widening it.
          sx={{ minWidth: responsiveValue<number | string>(0, 'auto') }}
        >
          <AppBarSpacer />
          <Outlet />
        </MainContent>
      </Root>
    </TimezoneProvider>
  );
};
