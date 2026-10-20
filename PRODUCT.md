# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Inferred from the request to use the existing Python attendance system in Chrome: a local Flask server with HTML, CSS, and JavaScript, backed by Pandas and Excel files.

## Users

College students building or demonstrating a beginner-level attendance management project, and the person responsible for entering attendance and reviewing student records.

## Product Purpose

Manage student registration, daily attendance, and attendance summaries in Excel using a small Python application. Success means the user can demonstrate the complete workflow locally in a browser and understand how the Python code handles the data.

## Product Positioning

The data is stored in readable Excel workbooks and processed with Pandas, so a learner can inspect the records alongside the Python operations.

## Operating Context

This is a local college project intended to run on a student's computer and be opened in Chrome. Included fictional sample records make the dashboard and reports demonstrable immediately.

## Capabilities and Constraints

Confirmed from the project brief: register, list, search, and edit students; mark attendance as Present, Absent, or On Leave; prevent duplicate IDs and date/student rows; correct attendance; filter and export reports; show a dashboard; use Students.xlsx, Attendance.xlsx, and Reports.xlsx rather than a database. Missing attendance is not automatically an absence. On Leave is excluded from the attendance percentage denominator. The web server is inferred to be local-only for this demonstration; deployment, authentication, and multi-user access are undecided.

## Evidence on Hand

The project includes fictional sample records in `Students.xlsx` and `Attendance.xlsx`. These are demonstration data, not real student records or evidence of deployment.

## Product Principles

- Keep the Python data operations readable to a beginner.
- Keep Excel as the visible, inspectable source of stored data.
- Make unrecorded attendance distinct from Absent.
- Give clear feedback when validation blocks an operation.
