Feature: Public Profile
  Tfriend's page shows information about the user
  And about their questions and answers

  Scenario: New user
    Given George is a registered user with no activity
    When I'm looking at friend's public profile
    Then I should see friend's username

  Scenario: User with question
    Given Fred asked a question
    When I'm looking at friend's public profile
    Then I should see friend's username (like before)
    And I should see his questions
    And a link to it
    And where he asked it

  Scenario: User with short answer
    Given Hermione answered a question briefly
    When I'm looking at her public profile
    Then I should see her details like before
    And the question she answered
    And a link to it
    And her answer

  Scenario: User with long answer
    Given Ginny answered a question verbosely
    Then I should see her details like before
    And the question she answered
    And a snippet of her answer
    And a link to the answer
