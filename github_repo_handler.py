import github
from getpass import getpass

LEETCODE_REPO_NAME="leetcode-accepted-submissions"
README="README.md"

"""
Convert language name to file extension
"""
def language_to_file_extension(language):
  if language.startswith('python'):
    return '.py'
  else:
    raise Exception(language+' to extension conversion not implemented')


"""
Responsible for creating and maintaining the github repo with leetcode submissions
"""
class GithubRepoHandler:
  def __init__(self):
    self.github = None

    username = input("Github username: ")
    password = getpass()

    self.github = github.Github(username, password)
    self.repo = None

  """
  creates leetcode submission repo if non existent
  """
  def create_repo(self):
    try:  
      self.repo = self.github.get_user().create_repo(LEETCODE_REPO_NAME)
    except github.GithubException as e:
      print(str(e)+": possible that the repo already exists")

  """
  returns leetcode submission repo
  """
  def repo_exists(self):
    if not self.repo:
      try:
        self.repo = self.github.get_user().get_repo(LEETCODE_REPO_NAME)
      except github.UnknownObjectException as e:
        print(str(e)+": repo does not exist")

    return self.repo

  """
  Takes a dict of problem_name to (accepted_url, language, code_content) and commits the code in a file <problem_name>.<ext>
  """
  def commit(self, latest_accepted_submissions):
    for k, v in latest_accepted_submissions.items():
      problem_name = k
      accepted_submission_url = v[0]
      language = v[1]
      code_contents = v[2]

      self.__update_readme(problem_name, accepted_submission_url)

      filename = problem_name + language_to_file_extension(language)

      # Try creating files first as it is more likely submissions will be made for new problems
      try:
        self.repo.create_file(filename, "Create "+filename, code_contents)
      except github.GithubException.GithubException:
        # File already exists
        contents = self.repo.get_contents(filename)
        self.repo.update_file(contents.path, "Update "+filename, code_contents, contents.sha)

  """
  collect and return accepted_submission urls from README
  """
  def get_commited_accepted_submission_urls(self):
    readme_content = self.__get_readme()
    file_content = readme_content.content
    lines = file_content.split("\n")
    urls = []
    for l in lines:
      if len(l.split(" ")) == 3:
        urls.append(l.split(" ")[2])
    return urls
 
  """
  Get readme file contents from repo or create if not existent
  """
  def __get_readme(self):
    try:
      readme_content = self.repo.get_contents(README)
    except github.GithubException as e:
      # If we cannot create README here just let the exception go since there it is something fatal
      readme_content = self.repo.create_file(README, "Create README", "# Leetcode Accepted Submissions")['content']

    return readme_content

  """
  Updates README with <problem_url> -> <accepted_url>
  """
  def __update_readme(self, problem_name, accepted_url):
    readme_content = self.__get_readme()
    file_content = readme_content.content
    if not accepted_url in file_content:
      new_content = file_content + "\n" + "https://leetcode.com/problems/"+problem_name+" -> "+accepted_url
      self.repo.update_file(readme_content.path, "Add "+accepted_url+" to README", new_content, readme_content.sha)