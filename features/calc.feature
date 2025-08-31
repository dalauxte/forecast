# language: de
Funktionalität: Forecast der Budgetverteilung pro Monat

        Szenario: Budget ist kleiner als verfügbare Kapazität
            Angenommen folgende Konfiguration liegt vor:
                  """
                  settings:
                    state: NI
                    planning_period:
                      start: 2025-09-01
                      end: 2025-12-31
                    round_hours: 0.15
                    locale: de-DE
                  
                  capacity:
                    per_weekday: { mon: 8, tue: 8, wed: 8, thu: 8, fri: 8 }
                    interval_overrides:
                      - { start: 2025-10-09, end: 2025-10-10, hours_per_day: 2 }   # Event im Oktober
                  
                  calendar:
                  vacation_days:
                      - { start: 2025-04-20, end: 2025-04-24 }   # Urlaub
                      # - 2025-10-20
                  holiday_overrides:
                      add: []
                      remove: []
                  
                  sickness:
                  prob_per_workday: 0.02   # 2% Ausfallwahrscheinlichkeit je Arbeitstag
                  
                  projects:
                  - name: ALH BAM
                      start: 2025-08-01
                      end: 2025-10-31
                      rest_budget_hours: 73.15
                      rate_eur_per_h: 174.0
                      weights_by_month:
                      "2025-09": 40   
                      "2025-10": 30   
                  
                  - name: ALH SEPO
                      start: 2025-08-01
                      end: 2025-12-31
                      rest_budget_hours: 270
                      rate_eur_per_h: 174.0
                      weights_by_month:
                      "2025-09": 60     
                      "2025-10": 70     
                  """

             Wenn die Sachbearbeitung nach "ANR-00042" oder dem Partner sucht
             Dann sehe ich eine durchgängige Timeline der BUW "E2E-1234" über alle beteiligten Systeme
              Und der aktuelle Status wird als "in Bearbeitung" mit den letzten Ereignissen angezeigt
              Und ich kann die letzten Schritte (z. B. "Auszahlung vorbereitet") benennen

        Szenario: Duplikate werden idempotent behandelt und nicht doppelt angezeigt
            Angenommen das Ereignis "Antrag eingereicht" zu "ANR-00042" trifft erneut ein
             Wenn die Ingestion die Nachricht verarbeitet
             Dann wird das Ereignis dedupliziert und erscheint nicht doppelt in der Timeline
              Und die fachliche Sicht auf den Prozess bleibt unverändert

        Szenario: Out-of-Order eingehende Ereignisse werden korrekt einsortiert
            Angenommen ein verspätetes Ereignis "Vorprüfung gestartet" mit Zeitstempel 2025-05-06 10:30:00 trifft ein
             Wenn die Ingestion die Nachricht persistiert
             Dann wird das Ereignis an der korrekten zeitlichen Position in der Timeline angezeigt
              Und Referenzen/Vorgänger bleiben konsistent, ohne die Reihenfolge zu verfälschen

        Szenario: Suche über Domänen nach Partner oder Vorgang
            Angenommen ich kenne nur die Partner- oder Vorgangsreferenz
             Wenn ich nach "VG-88421" suche
             Dann finde ich die zugehörige BUW "E2E-1234" und sehe verbundene Ereignisse
              Und ich kann zwischen Partner-, Vorgangs- und BUW-Sicht wechseln

        Szenario: Transparente Degradierung bei Störung der Event-Verarbeitung
            Angenommen RabbitMQ ist vorübergehend nicht erreichbar
             Wenn BAM keine neuen Ereignisse empfangen kann
             Dann ist der Systemzustand für Betrieb/Observability ersichtlich (z. B. Health-Status/Alarm)
              Und ein Backlog wird aufgestaut und nach Wiederherstellung abgearbeitet
              Und Nutzer sehen einen Hinweis, dass Daten ggf. verzögert sind

        Szenario: Schnelle Abrufbarkeit innerhalb der Vorhaltefrist
            Angenommen ich rufe die Timeline der letzten 24 Monate für "E2E-1234" ab
             Wenn ich die Ereignisse anzeige
             Dann erfolgt die Darstellung ohne spürbare Wartezeit innerhalb der vereinbarten Vorhaltefrist
              Und ältere Daten außerhalb der Frist sind nicht Teil der operativen Auskunft