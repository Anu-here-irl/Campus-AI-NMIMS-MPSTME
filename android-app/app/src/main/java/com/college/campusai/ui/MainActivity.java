package com.college.campusai.ui;

import android.content.Intent;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentTransaction;

import com.college.campusai.CampusAiApp;
import com.college.campusai.R;
import com.college.campusai.utils.SessionManager;
import com.google.android.material.bottomnavigation.BottomNavigationView;

public class MainActivity extends AppCompatActivity {

    private BottomNavigationView bottomNav;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        SessionManager sessionManager = CampusAiApp.getInstance().getSessionManager();
        if (!sessionManager.isLoggedIn()) {
            startActivity(new Intent(this, LoginActivity.class));
            finish();
            return;
        }

        setContentView(R.layout.activity_main);

        bottomNav = findViewById(R.id.bottom_navigation);
        bottomNav.setOnItemSelectedListener(item -> {
            int itemId = item.getItemId();
            if (itemId == R.id.nav_dashboard) {
                loadFragment(new DashboardFragment());
                return true;
            } else if (itemId == R.id.nav_emails) {
                loadFragment(new EmailsFragment());
                return true;
            } else if (itemId == R.id.nav_timetable) {
                loadFragment(new TimetableFragment());
                return true;
            } else if (itemId == R.id.nav_chat) {
                loadFragment(new ChatFragment());
                return true;
            } else if (itemId == R.id.nav_map) {
                loadFragment(new CampusMapFragment());
                return true;
            }
            return false;
        });

        if (savedInstanceState == null) {
            loadFragment(new DashboardFragment());
        }
    }

    public void switchToTab(int navItemId) {
        if (bottomNav != null) {
            bottomNav.setSelectedItemId(navItemId);
        }
    }

    /**
     * Navigate to the Campus Map tab and auto-highlight a specific room.
     * Called from TimetableFragment's "View in Map" context menu option.
     */
    public void navigateToMap(String roomCode, String floorId) {
        CampusMapFragment mapFragment = CampusMapFragment.newInstance(roomCode, floorId);
        if (bottomNav != null) {
            bottomNav.setSelectedItemId(R.id.nav_map);
        }
        getSupportFragmentManager().beginTransaction()
                .replace(R.id.fragment_container, mapFragment)
                .commit();
    }

    private void loadFragment(Fragment fragment) {
        FragmentTransaction transaction = getSupportFragmentManager().beginTransaction();
        transaction.replace(R.id.fragment_container, fragment);
        transaction.commit();
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        menu.add(0, 101, 0, "Sign Out").setShowAsAction(MenuItem.SHOW_AS_ACTION_NEVER);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        if (item.getItemId() == 101) {
            CampusAiApp.getInstance().getSessionManager().clear();
            startActivity(new Intent(this, LoginActivity.class));
            finish();
            return true;
        }
        return super.onOptionsItemSelected(item);
    }
}
