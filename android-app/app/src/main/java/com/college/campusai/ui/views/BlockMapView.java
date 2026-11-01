package com.college.campusai.ui.views;

import android.animation.ValueAnimator;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.Rect;
import android.graphics.RectF;
import android.util.AttributeSet;
import android.view.GestureDetector;
import android.view.MotionEvent;
import android.view.ScaleGestureDetector;
import android.view.View;
import android.view.animation.DecelerateInterpolator;


import com.college.campusai.models.CampusMapModels.FloorPlan;
import com.college.campusai.models.CampusMapModels.RoomBlock;

public class BlockMapView extends View {

    public interface OnRoomSelectedListener {
        void onRoomSelected(RoomBlock room);
        void onSelectionCleared();
    }

    private FloorPlan currentFloor;
    private RoomBlock selectedRoom;
    private RoomBlock highlightedRoom;
    private OnRoomSelectedListener listener;

    // Drawing Paints
    private Paint fillPaint;
    private Paint strokePaint;
    private Paint textCodePaint;
    private Paint textNamePaint;
    private Paint badgePaint;
    private Paint badgeTextPaint;
    private Paint backgroundPaint;
    private Paint floorBoundaryPaint;
    private Paint floorShadowPaint;

    // Transformations
    private final Matrix transformMatrix = new Matrix();
    private final Matrix inverseMatrix = new Matrix();
    private final float[] matrixValues = new float[9];
    private float currentScale = 1.0f;
    private float minScale = 0.2f;
    private float maxScale = 5.0f;

    // Gesture Detectors
    private ScaleGestureDetector scaleDetector;
    private GestureDetector gestureDetector;

    public BlockMapView(Context context) {
        super(context);
        init(context);
    }

    public BlockMapView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init(context);
    }

    public BlockMapView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        init(context);
    }

    private void init(Context context) {
        fillPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        fillPaint.setStyle(Paint.Style.FILL);

        strokePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        strokePaint.setStyle(Paint.Style.STROKE);
        strokePaint.setStrokeWidth(2f);

        textCodePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        textCodePaint.setColor(Color.parseColor("#0F172A"));
        textCodePaint.setTextSize(14f);
        textCodePaint.setFakeBoldText(true);
        textCodePaint.setTextAlign(Paint.Align.CENTER);

        textNamePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        textNamePaint.setColor(Color.parseColor("#334155"));
        textNamePaint.setTextSize(11f);
        textNamePaint.setTextAlign(Paint.Align.CENTER);

        badgePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        badgePaint.setStyle(Paint.Style.FILL);
        badgePaint.setColor(Color.parseColor("#D97706"));

        badgeTextPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        badgeTextPaint.setColor(Color.WHITE);
        badgeTextPaint.setTextSize(9f);
        badgeTextPaint.setFakeBoldText(true);
        badgeTextPaint.setTextAlign(Paint.Align.CENTER);

        backgroundPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        backgroundPaint.setStyle(Paint.Style.FILL);
        backgroundPaint.setColor(Color.parseColor("#F8FAFC"));

        floorBoundaryPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        floorBoundaryPaint.setStyle(Paint.Style.STROKE);
        floorBoundaryPaint.setColor(Color.parseColor("#CBD5E1"));
        floorBoundaryPaint.setStrokeWidth(3f);

        floorShadowPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        floorShadowPaint.setStyle(Paint.Style.FILL);
        floorShadowPaint.setColor(Color.parseColor("#E2E8F0"));

        scaleDetector = new ScaleGestureDetector(context, new ScaleListener());
        gestureDetector = new GestureDetector(context, new GestureListener());
    }

    public void setOnRoomSelectedListener(OnRoomSelectedListener listener) {
        this.listener = listener;
    }

    public void setFloorPlan(FloorPlan floorPlan) {
        this.currentFloor = floorPlan;
        this.selectedRoom = null;
        this.highlightedRoom = null;
        if (listener != null) {
            listener.onSelectionCleared();
        }
        post(this::fitToScreen);
    }

    public FloorPlan getCurrentFloor() {
        return currentFloor;
    }

    public void selectRoom(RoomBlock room) {
        this.selectedRoom = room;
        invalidate();
        if (listener != null) {
            if (room != null) {
                listener.onRoomSelected(room);
            } else {
                listener.onSelectionCleared();
            }
        }
    }

    public void highlightRoom(RoomBlock room) {
        this.highlightedRoom = room;
        selectRoom(room);
        if (room != null) {
            zoomToRoom(room);
        } else {
            invalidate();
        }
    }

    public void clearHighlight() {
        this.highlightedRoom = null;
        this.selectedRoom = null;
        invalidate();
        if (listener != null) {
            listener.onSelectionCleared();
        }
    }

    public void fitToScreen() {
        if (currentFloor == null || getWidth() <= 0 || getHeight() <= 0) {
            return;
        }

        float viewWidth = getWidth();
        float viewHeight = getHeight();
        float floorWidth = currentFloor.width > 0 ? currentFloor.width : 1000f;
        float floorHeight = currentFloor.height > 0 ? currentFloor.height : 1350f;

        float padding = 40f;
        float scaleX = (viewWidth - (padding * 2)) / floorWidth;
        float scaleY = (viewHeight - (padding * 2)) / floorHeight;
        float targetScale = Math.min(scaleX, scaleY);

        minScale = Math.max(0.1f, targetScale * 0.5f);
        maxScale = Math.max(3.0f, targetScale * 6.0f);
        currentScale = targetScale;

        float targetDx = (viewWidth - (floorWidth * targetScale)) / 2f;
        float targetDy = (viewHeight - (floorHeight * targetScale)) / 2f;

        transformMatrix.reset();
        transformMatrix.postScale(targetScale, targetScale);
        transformMatrix.postTranslate(targetDx, targetDy);
        invalidate();
    }

    public void zoomToRoom(RoomBlock room) {
        if (room == null || getWidth() <= 0 || getHeight() <= 0) return;

        float roomCenterX = room.x + (room.width / 2f);
        float roomCenterY = room.y + (room.height / 2f);

        float viewWidth = getWidth();
        float viewHeight = getHeight();

        // Calculate desirable zoom level
        float targetScale = Math.max(currentScale * 1.6f, 1.2f);
        if (targetScale > maxScale) targetScale = maxScale;

        float targetDx = (viewWidth / 2f) - (roomCenterX * targetScale);
        float targetDy = (viewHeight / 2f) - (roomCenterY * targetScale);

        // Smooth animated transition
        transformMatrix.getValues(matrixValues);
        float startScale = matrixValues[Matrix.MSCALE_X];
        float startDx = matrixValues[Matrix.MTRANS_X];
        float startDy = matrixValues[Matrix.MTRANS_Y];

        ValueAnimator animator = ValueAnimator.ofFloat(0f, 1f);
        animator.setDuration(350);
        animator.setInterpolator(new DecelerateInterpolator());
        final float finalTargetScale = targetScale;
        animator.addUpdateListener(animation -> {
            float frac = (float) animation.getAnimatedValue();
            float currScale = startScale + (finalTargetScale - startScale) * frac;
            float currDx = startDx + (targetDx - startDx) * frac;
            float currDy = startDy + (targetDy - startDy) * frac;

            transformMatrix.reset();
            transformMatrix.postScale(currScale, currScale);
            transformMatrix.postTranslate(currDx, currDy);
            currentScale = currScale;
            invalidate();
        });
        animator.start();
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);
        if (currentFloor != null && (oldw == 0 || oldh == 0)) {
            fitToScreen();
        }
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        boolean handled = scaleDetector.onTouchEvent(event);
        handled = gestureDetector.onTouchEvent(event) || handled;
        return handled || super.onTouchEvent(event);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        if (currentFloor == null) {
            Paint emptyPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
            emptyPaint.setColor(Color.parseColor("#64748B"));
            emptyPaint.setTextSize(16f * getResources().getDisplayMetrics().density);
            emptyPaint.setTextAlign(Paint.Align.CENTER);
            canvas.drawText("Select a floor to view room blocks", getWidth() / 2f, getHeight() / 2f, emptyPaint);
            return;
        }

        canvas.save();
        canvas.concat(transformMatrix);

        float floorW = currentFloor.width > 0 ? currentFloor.width : 1000f;
        float floorH = currentFloor.height > 0 ? currentFloor.height : 1350f;

        // Draw Floor Canvas Backdrop
        RectF floorRect = new RectF(0, 0, floorW, floorH);
        canvas.drawRoundRect(new RectF(4, 4, floorW + 6, floorH + 6), 16f, 16f, floorShadowPaint);
        canvas.drawRoundRect(floorRect, 16f, 16f, backgroundPaint);
        canvas.drawRoundRect(floorRect, 16f, 16f, floorBoundaryPaint);

        // Draw Architectural Circulation Corridors (Walkways)
        Paint corridorPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        corridorPaint.setColor(Color.parseColor("#EDF2F7"));
        corridorPaint.setStyle(Paint.Style.FILL);

        Paint corridorLinePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        corridorLinePaint.setColor(Color.parseColor("#E2E8F0"));
        corridorLinePaint.setStyle(Paint.Style.STROKE);
        corridorLinePaint.setStrokeWidth(1.5f);

        // West Corridor (Between West Classrooms and Central Atrium)
        RectF westCorridor = new RectF(280f, 180f, 310f, 850f);
        canvas.drawRoundRect(westCorridor, 6f, 6f, corridorPaint);
        canvas.drawRoundRect(westCorridor, 6f, 6f, corridorLinePaint);

        // East Corridor (Between Central Atrium and East Labs/Offices)
        RectF eastCorridor = new RectF(690f, 180f, 720f, 850f);
        canvas.drawRoundRect(eastCorridor, 6f, 6f, corridorPaint);
        canvas.drawRoundRect(eastCorridor, 6f, 6f, corridorLinePaint);

        // Cross Walkways (Connecting Corridors)
        RectF northWalkway = new RectF(280f, 180f, 720f, 200f);
        canvas.drawRoundRect(northWalkway, 4f, 4f, corridorPaint);
        RectF southWalkway = new RectF(280f, 730f, 720f, 750f);
        canvas.drawRoundRect(southWalkway, 4f, 4f, corridorPaint);

        // Draw Room Blocks
        if (currentFloor.rooms != null) {
            for (RoomBlock room : currentFloor.rooms) {
                drawRoomBlock(canvas, room);
            }
        }

        canvas.restore();
    }

    private void drawRoomBlock(Canvas canvas, RoomBlock room) {
        RectF rect = new RectF(room.x, room.y, room.x + room.width, room.y + room.height);
        float radius = 10f;

        boolean isHighlighted = (highlightedRoom != null && highlightedRoom.code.equalsIgnoreCase(room.code));
        boolean isSelected = (selectedRoom != null && selectedRoom.code.equalsIgnoreCase(room.code));

        // Fill
        if (isHighlighted) {
            fillPaint.setColor(Color.parseColor("#FEF08A")); // Bright Amber/Yellow
        } else if (isSelected) {
            fillPaint.setColor(Color.parseColor("#DBEAFE")); // Soft Blue
        } else {
            fillPaint.setColor(room.getFillColor());
        }
        canvas.drawRoundRect(rect, radius, radius, fillPaint);

        // Stroke
        if (isHighlighted) {
            strokePaint.setColor(Color.parseColor("#B45309")); // Deep Amber
            strokePaint.setStrokeWidth(5f);
        } else if (isSelected) {
            strokePaint.setColor(Color.parseColor("#1D4ED8")); // Deep Blue
            strokePaint.setStrokeWidth(4f);
        } else {
            strokePaint.setColor(room.getBorderColor());
            strokePaint.setStrokeWidth(2.5f);
        }
        canvas.drawRoundRect(rect, radius, radius, strokePaint);

        // Draw Labels clipped inside the room block to prevent any jumbled text overflow
        canvas.save();
        canvas.clipRect(new RectF(rect.left + 3f, rect.top + 3f, rect.right - 3f, rect.bottom - 3f));

        float centerX = rect.centerX();
        float centerY = rect.centerY();

        if (room.height >= 55 && room.width >= 60) {
            // Draw Room Code centered above centerY
            float codeSize = Math.max(9.5f, Math.min(13.5f, room.width * 0.14f));
            textCodePaint.setTextSize(codeSize);
            canvas.drawText(room.code != null ? room.code : "", centerX, centerY - 2, textCodePaint);

            // Draw Short Name centered below centerY
            String displayName = room.name;
            if (displayName != null) {
                int maxChars = Math.max(10, (int) (room.width / 11f));
                if (displayName.length() > maxChars) {
                    displayName = displayName.substring(0, maxChars - 2) + "..";
                }
            }
            float nameSize = Math.max(8.5f, Math.min(10.5f, room.width * 0.10f));
            textNamePaint.setTextSize(nameSize);
            canvas.drawText(displayName != null ? displayName : "", centerX, centerY + 14, textNamePaint);
        } else {
            // Compact single line code
            float codeSize = Math.max(8.5f, Math.min(11.5f, room.width * 0.18f));
            textCodePaint.setTextSize(codeSize);
            canvas.drawText(room.code != null ? room.code : "", centerX, centerY + 4, textCodePaint);
        }

        canvas.restore();

        // Draw verification badge if unverified
        if (!room.verified) {
            float badgeX = rect.right - 14f;
            float badgeY = rect.top + 14f;
            canvas.drawCircle(badgeX, badgeY, 8f, badgePaint);
            canvas.drawText("?", badgeX, badgeY + 3f, badgeTextPaint);
        }
    }

    private class ScaleListener extends ScaleGestureDetector.SimpleOnScaleGestureListener {
        @Override
        public boolean onScale(ScaleGestureDetector detector) {
            float scaleFactor = detector.getScaleFactor();
            float newScale = currentScale * scaleFactor;

            if (newScale >= minScale && newScale <= maxScale) {
                currentScale = newScale;
                transformMatrix.postScale(scaleFactor, scaleFactor, detector.getFocusX(), detector.getFocusY());
                invalidate();
            }
            return true;
        }
    }

    private class GestureListener extends GestureDetector.SimpleOnGestureListener {
        @Override
        public boolean onScroll(MotionEvent e1, MotionEvent e2, float distanceX, float distanceY) {
            transformMatrix.postTranslate(-distanceX, -distanceY);
            invalidate();
            return true;
        }

        @Override
        public boolean onSingleTapUp(MotionEvent e) {
            if (currentFloor == null || currentFloor.rooms == null) return false;

            transformMatrix.invert(inverseMatrix);
            float[] pts = new float[]{e.getX(), e.getY()};
            inverseMatrix.mapPoints(pts);
            float worldX = pts[0];
            float worldY = pts[1];

            RoomBlock clickedRoom = null;
            // Iterate in reverse so topmost rooms get priority
            for (int i = currentFloor.rooms.size() - 1; i >= 0; i--) {
                RoomBlock r = currentFloor.rooms.get(i);
                if (r.containsPoint(worldX, worldY)) {
                    clickedRoom = r;
                    break;
                }
            }

            if (clickedRoom != null) {
                highlightedRoom = clickedRoom;
                selectRoom(clickedRoom);
            } else {
                clearHighlight();
            }
            return true;
        }

        @Override
        public boolean onDoubleTap(MotionEvent e) {
            if (currentFloor == null) return false;

            float targetScale = currentScale > 1.5f ? 1.0f : 2.2f;
            float factor = targetScale / currentScale;
            currentScale = targetScale;
            transformMatrix.postScale(factor, factor, e.getX(), e.getY());
            invalidate();
            return true;
        }
    }
}
