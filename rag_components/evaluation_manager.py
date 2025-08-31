from langchain_core.documents import Document
from datetime import datetime


class EmployeeEvaluation:
    """Employee evaluation data structure"""
    
    def __init__(self, employee_id, evaluator, period, content, score, metadata=None, goals=None):
        self.employee_id = employee_id
        self.evaluator = evaluator
        self.period = period
        self.content = content
        self.score = score
        self.metadata = metadata or {}
        self.goals = goals or []
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()


class EvaluationManager:
    """Manage employee evaluations"""
    
    def __init__(self):
        self.evaluations = []
    
    def add_evaluation(self, evaluation):
        """Add an evaluation to the manager"""
        self.evaluations.append(evaluation)
    
    def update_evaluation(self, employee_id, period, **kwargs):
        """Update an existing evaluation"""
        for eval in self.evaluations:
            if eval.employee_id == employee_id and eval.period == period:
                for key, value in kwargs.items():
                    if hasattr(eval, key):
                        setattr(eval, key, value)
                eval.updated_at = datetime.now().isoformat()
                return True
        return False
    
    def get_evaluations_by_employee(self, employee_id):
        """Get all evaluations for an employee"""
        return [e for e in self.evaluations if e.employee_id == employee_id]
    
    def get_evaluations_by_period(self, period):
        """Get all evaluations for a period"""
        return [e for e in self.evaluations if e.period == period]
    
    def get_evaluation(self, employee_id, period):
        """Get a specific evaluation"""
        for eval in self.evaluations:
            if eval.employee_id == employee_id and eval.period == period:
                return eval
        return None
    
    def get_average_score(self, employee_id):
        """Calculate average score for an employee"""
        employee_evals = self.get_evaluations_by_employee(employee_id)
        if not employee_evals:
            return 0
        return sum([e.score for e in employee_evals]) / len(employee_evals)
    
    def get_evaluations_summary(self, employee_id):
        """Get a summary of all evaluations for an employee"""
        employee_evals = self.get_evaluations_by_employee(employee_id)
        if not employee_evals:
            return "Nenhuma avaliação encontrada."
        
        avg_score = self.get_average_score(employee_id)
        total_evals = len(employee_evals)
        
        summary = f"Resumo de Avaliações para o Funcionário {employee_id}:\n"
        summary += f"- Total de avaliações: {total_evals}\n"
        summary += f"- Nota média: {avg_score:.2f}\n\n"
        
        for eval in employee_evals:
            summary += f"Período: {eval.period}\n"
            summary += f"Nota: {eval.score}\n"
            summary += f"Avaliador: {eval.evaluator}\n\n"
        
        return summary
    
    def to_documents(self):
        """Convert evaluations to LangChain documents for vector storage"""
        documents = []
        for eval in self.evaluations:
            content = f"""
            Avaliação de Funcionário
            ID do Funcionário: {eval.employee_id}
            Avaliador: {eval.evaluator}
            Período: {eval.period}
            Nota: {eval.score}
            Conteúdo: {eval.content}
            Metas: {", ".join(eval.goals) if eval.goals else "Nenhuma"}
            """
            
            metadata = {
                "type": "employee_evaluation",
                "employee_id": eval.employee_id,
                "evaluator": eval.evaluator,
                "period": eval.period,
                "score": eval.score,
                "created_at": eval.created_at,
                "updated_at": eval.updated_at
            }
            
            metadata.update(eval.metadata)
            
            doc = Document(page_content=content, metadata=metadata)
            documents.append(doc)
        
        return documents