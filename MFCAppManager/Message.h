#pragma once


// Message 对话框

class Message : public CDialogEx
{
	DECLARE_DYNAMIC(Message)

public:
	Message(CWnd* pParent = NULL);   // 标准构造函数
	virtual ~Message();

// 对话框数据
#ifdef AFX_DESIGN_TIME
	enum { IDD = IDD_DIALOG_MESSAGE };
#endif

protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV 支持

	DECLARE_MESSAGE_MAP()
public:
	afx_msg void OnEnChangeEditnameNewName();
	afx_msg void OnEnChangeStaticExplevelS();
	afx_msg void OnEnChangeEditpointS();
	afx_msg void OnEnChangeEditpointHoldS();
	afx_msg void OnEnChangeEditpointexpS();
	afx_msg void OnEnChangeEditnameNew2S();
	afx_msg void OnEnChangeEditnameNew3S();
	afx_msg void OnEnChangeEditnameNewIdS();
	afx_msg void UpData(CString name, CString level, CString point, CString money, CString expall, CString sex, CString camp, CString user_id);
	CString m_name;
	CString m_level;
	CString m_point;
	CString m_money;
	CString m_expall;
	CString m_sex;
	CString m_camp;
	CString m_user_id;
};
